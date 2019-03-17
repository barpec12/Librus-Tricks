from datetime import datetime


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
        """
        Klasa reprezentująca nauczyciela

        :type session: librus_tricks.core.SynergiaClient
        """
        super().__init__(oid, session, ('Users',), 'User', payload)
        self.name = self.json_payload['FirstName']
        self.last_name = self.json_payload['LastName']


class SynergiaStudent(SynergiaTeacher):
    pass


class SynergiaClass(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        """
        Klasa reprezentująca klasę (jako zbiór uczniów)

        :type session: librus_tricks.core.SynergiaClient
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
        self.add_date = datetime.strptime(self.json_payload['AddDate'], '%Y-%m-%d %H:%M:%S')
        self.grade = self.json_payload['Grade']
        self.have_influence = self.json_payload['IsConstituent']
        self.semester = self.json_payload['Semester']

    @property
    def teacher(self):
        return SynergiaTeacher(self.json_payload['AddedBy']['Id'], self._session)

    @property
    def subject(self):
        return SynergiaSubject(self.json_payload['Subject']['Id'], self._session)

    @property
    def comments(self):
        if 'Comments' in self.json_payload.keys():
            grade_comments = []
            for c in self.json_payload['Comments']:
                grade_comments.append(SynergiaGradeComment(c['Id'], self._session))
            return tuple(grade_comments)
        else:
            return tuple()


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
