from datetime import datetime


def _try_to_extract(payload, extraction_key):
    if extraction_key in payload.keys():
        return payload[extraction_key]
    else:
        return None


class SynergiaGenericClass:
    def __init__(self, oid, session, resource, extraction_key, payload=None):
        self._session = session
        self.oid = oid
        if payload == None:
            self.json_payload = self._session.get(
                *resource,
                self.oid
            )[extraction_key]
        else:
            self.json_payload = payload

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.oid}>'


class SynergiaTeacher(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('Users',), 'User', payload)
        self.name = self.json_payload['FirstName']
        self.last_name = self.json_payload['LastName']


class SynergiaStudent(SynergiaTeacher):
    pass


class SynergiaClass(SynergiaGenericClass):
    """Klasa reprezentująca klasę"""
    def __init__(self, oid, session, payload=None):
        """
        Tworzy obiekt reprezentujący klasę (jako zbiór uczniów)

        :param str oid: id klasy
        :param librus_tricks.core.SynergiaClient session: obiekt sesji z API Synergii
        :param dict payload: dane z json'a
        """
        super().__init__(oid, session, ('Classes',), 'Class', payload)
        self.alias = f'{self.json_payload["Number"]}{self.json_payload["Symbol"]}'
        self.begin_date = datetime.strptime(self.json_payload['BeginSchoolYear'], '%Y-%m-%d')
        self.end_date = datetime.strptime(self.json_payload['EndSchoolYear'], '%Y-%m-%d')

    @property
    def tutor(self):
        return SynergiaTeacher(self.json_payload['ClassTutor']['Id'], self._session)


class SynergiaSubject(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('Subjects',), 'Subject', payload)
        self.name = self.json_payload['Name']
        self.short_name = self.json_payload['Short']


class SynergiaLesson(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        """
        Klasa reprezentująca jednostkową lekcję

        :type session: librus_tricks.core.SynergiaClient
        """
        super().__init__(oid, session, ('Users',), 'User', payload)

    @property
    def teacher(self):
        return SynergiaTeacher(self.json_payload['Teacher']['Id'], self._session)

    @property
    def group(self):
        return SynergiaClass(self.json_payload['Class']['Id'], self._session)

    @property
    def subject(self):
        return SynergiaSubject(self.json_payload['Subject']['Id'], self._session)


class SynergiaGradeCategory(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('Grades', 'Categories',), 'Category', payload)
        self.count_to_the_average = self.json_payload['CountToTheAverage']
        self.name = self.json_payload['Name']
        self.obligation_to_perform = self.json_payload['ObligationToPerform']
        self.standard = self.json_payload['Standard']
        self.weight = _try_to_extract(self.json_payload, 'Weight')

    @property
    def for_lessons(self):
        return [SynergiaLesson(x['Id'], self._session) for x in self.json_payload['ForLessons']]

    @property
    def teacher(self):
        return SynergiaTeacher(self.json_payload['Teacher']['Id'], self._session)


class SynergiaGradeComment(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('Grades', 'Comments',), 'Comment', payload)
        self.text = self.json_payload['Text']

    @property
    def teacher(self):
        return SynergiaTeacher(self.json_payload['AddedBy']['Id'], self._session)

    @property
    def grade_bind(self):
        return SynergiaGrade(self.json_payload['Grade']['Id'], self._session)


class SynergiaGrade(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('Grades',), 'Grade', payload)

        class GradeMetadata:
            def __init__(self, is_c, is_s, is_sp, is_f, is_fp):
                self.is_constituent = is_c
                self.is_semester_grade = is_s
                self.is_semester_grade_proposition = is_sp
                self.is_final_grade = is_f
                self.is_final_grade_proposition = is_fp

        self.add_date = datetime.strptime(self.json_payload['AddDate'], '%Y-%m-%d %H:%M:%S')
        self.date = datetime.strptime(self.json_payload['Date'], '%Y-%m-%d')
        self.grade = self.json_payload['Grade']
        self.is_constituent = self.json_payload['IsConstituent']
        self.semester = self.json_payload['Semester']
        self.metadata = GradeMetadata(
            self.json_payload['IsConstituent'],
            self.json_payload['IsSemester'],
            self.json_payload['IsSemesterProposition'],
            self.json_payload['IsFinal'],
            self.json_payload['IsFinalProposition']
        )

    @property
    def teacher(self):
        return SynergiaTeacher(self.json_payload['AddedBy']['Id'], self._session)

    @property
    def subject(self):
        return SynergiaSubject(self.json_payload['Subject']['Id'], self._session)

    @property
    def comments(self):
        if 'Comments' in self.json_payload.keys():
            return [SynergiaGradeComment(x['Id'], self._session) for x in self.json_payload['Comments']]
        else:
            return []

    @property
    def category(self):
        return SynergiaGradeCategory(self.json_payload['Category']['Id'], self._session)


class SynergiaAttendanceType(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('Attendances', 'Types',), 'Type', payload)
        self.color = self.json_payload['ColorRGB']
        self.is_presence_kind = self.json_payload['IsPresenceKind']
        self.name = self.json_payload['Name']
        self.short_name = self.json_payload['Short']

    def __repr__(self):
        return f'<SynergiaAttendanceType {self.short_name}>'


class SynergiaAttendance(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('Attendances',), 'Attendance', payload)
        self.add_date = datetime.strptime(self.json_payload['AddDate'], '%Y-%m-%d %H:%M:%S')
        self.date = datetime.strptime(self.json_payload['Date'], '%Y-%m-%d')
        self.lesson_no = self.json_payload['LessonNo']

    @property
    def teacher(self):
        return SynergiaTeacher(self.json_payload['AddedBy']['Id'], self._session)

    @property
    def student(self):
        return SynergiaStudent(self.json_payload['Student']['Id'], self._session)

    @property
    def type(self):
        return SynergiaAttendanceType(self.json_payload['Type']['Id'], self._session)

    def __repr__(self):
        return f'<SynergiaAttendance at {self.add_date}>'
