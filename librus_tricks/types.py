from datetime import datetime


class SynergiaGenericClass:
    def __init__(self, oid, session, resource, extraction_key, payload=None):
        self._session = session
        self.oid = oid
        if payload == None:
            self._payload = self._session.get(
                *resource,
                self.oid
            )[extraction_key]
        else:
            self._payload = payload


    def __repr__(self):
        return f'<{self.__class__.__name__} {self.oid}>'


class SynergiaTeacher(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        """
        Klasa reprezentująca nauczyciela

        :type session: librus_tricks.core.SynergiaClient
        """
        super().__init__(oid, session, ('Users',), 'User', payload)
        self.name = self._payload['FirstName']
        self.last_name = self._payload['LastName']


class SynergiaStudent(SynergiaTeacher):
    pass


class SynergiaClass(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        """
        Klasa reprezentująca klasę (jako zbiór uczniów)

        :type session: librus_tricks.core.SynergiaClient
        """
        super().__init__(oid, session, ('Classes',), 'Class', payload)
        self.alias = f'{self._payload["Number"]}{self._payload["Symbol"]}'
        self.begin_date = datetime.strptime(self._payload['BeginSchoolYear'], '%Y-%m-%d')
        self.end_date = datetime.strptime(self._payload['EndSchoolYear'], '%Y-%m-%d')

    @property
    def tutor(self):
        return SynergiaTeacher(self._payload['ClassTutor']['Id'], self._session)


class SynergiaSubject(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('Subjects',), 'Subject', payload)
        self.name = self._payload['Name']
        self.short_name = self._payload['Short']


class SynergiaLesson(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        """
        Klasa reprezentująca jednostkową lekcję

        :type session: librus_tricks.core.SynergiaClient
        """
        super().__init__(oid, session, ('Users',), 'User', payload)

    @property
    def teacher(self):
        return SynergiaTeacher(self._payload['Teacher']['Id'], self._session)

    @property
    def group(self):
        return SynergiaClass(self._payload['Class']['Id'], self._session)

    @property
    def subject(self):
        return SynergiaSubject(self._payload['Subject']['Id'], self._session)


class SynergiaGradeComment(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('Grades', 'Comments',), 'Comment', payload)
        self.text = self._payload['Text']

    @property
    def teacher(self):
        return SynergiaTeacher(self._payload['AddedBy']['Id'], self._session)

    @property
    def grade_bind(self):
        return SynergiaGrade(self._payload['Grade']['Id'], self._session)


class SynergiaGrade(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('Grades',), 'Grade', payload)
        self.add_date = datetime.strptime(self._payload['AddDate'], '%Y-%m-%d %H:%M:%S')
        self.grade = self._payload['Grade']
        self.have_influence = self._payload['IsConstituent']
        self.semester = self._payload['Semester']

    @property
    def teacher(self):
        return SynergiaTeacher(self._payload['AddedBy']['Id'], self._session)

    @property
    def subject(self):
        return SynergiaSubject(self._payload['Subject']['Id'], self._session)

    @property
    def comments(self):
        grade_comments = []
        for c in self._payload['Comments']:
            grade_comments.append(SynergiaGradeComment(c['Id'], self._session))
        return grade_comments


class SynergiaAttendanceType(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('Attendances', 'Types',), 'Type', payload)
        self.color = self._payload['ColorRGB']
        self.is_presence_kind = self._payload['IsPresenceKind']
        self.name = self._payload['Name']


class SynergiaAttendance(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('Attendances',), 'Attendance', payload)
        self.add_date = datetime.strptime(self._payload['AddDate'], '%Y-%m-%d %H:%M:%S')
        self.lesson_no = self._payload['LessonNo']

    @property
    def teacher(self):
        return SynergiaTeacher(self._payload['AddedBy']['Id'], self._session)

    @property
    def student(self):
        return SynergiaStudent(self._payload['Student']['Id'], self._session)

    @property
    def type(self):
        return SynergiaAttendanceType(self._payload['Type']['Id'], self._session)
