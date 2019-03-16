from datetime import datetime


class SynergiaGenericClass:
    def __init__(self, oid, session):
        self._session = session
        self.oid = oid

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.oid}>'


class SynergiaTeacher(SynergiaGenericClass):
    def __init__(self, oid, session):
        """
        Klasa reprezentująca nauczyciela

        :type session: librus_tricks.core.SynergiaClient
        """
        super().__init__(oid, session)
        self.__payload = session.get('Users', oid)['User']
        self.name = self.__payload['FirstName']
        self.last_name = self.__payload['LastName']


class SynergiaStudent(SynergiaTeacher):
    pass


class SynergiaClass(SynergiaGenericClass):
    def __init__(self, oid, session):
        """
        Klasa reprezentująca klasę (jako zbiór uczniów)

        :type session: librus_tricks.core.SynergiaClient
        """
        super().__init__(oid, session)
        self.__payload = session.get('Classes', oid)['Class']
        self.alias = f'{self.__payload["Number"]}{self.__payload["Symbol"]}'
        self.begin_date = datetime.strptime(self.__payload['BeginSchoolYear'], '%Y-%m-%d')
        self.end_date = datetime.strptime(self.__payload['EndSchoolYear'], '%Y-%m-%d')

    @property
    def tutor(self):
        return SynergiaTeacher(self.__payload['ClassTutor']['Id'], self._session)


class SynergiaSubject(SynergiaGenericClass):
    def __init__(self, oid, session):
        super().__init__(oid, session)
        self.__payload = session.get('Subjects', oid)['Subject']
        self.name = self.__payload['Name']
        self.short_name = self.__payload['Short']


class SynergiaLesson(SynergiaGenericClass):
    def __init__(self, oid, session):
        """
        Klasa reprezentująca jednostkową lekcję

        :type session: librus_tricks.core.SynergiaClient
        """
        super().__init__(oid, session)
        self.__payload = session.get('Users', oid)['User']

    @property
    def teacher(self):
        return SynergiaTeacher(self.__payload['Teacher']['Id'], self._session)

    @property
    def group(self):
        return SynergiaClass(self.__payload['Class']['Id'], self._session)

    @property
    def subject(self):
        return SynergiaSubject(self.__payload['Subject']['Id'], self._session)


class SynergiaGradeComment(SynergiaGenericClass):
    def __init__(self, oid, session):
        super().__init__(oid, session)
        self.__payload = session.get('Grades', 'Comments', oid)['Comment']
        self.text = self.__payload['Text']

    @property
    def teacher(self):
        return SynergiaTeacher(self.__payload['AddedBy']['Id'], self._session)

    @property
    def grade_bind(self):
        return SynergiaGrade(self.__payload['Grade']['Id'], self._session)


class SynergiaGrade(SynergiaGenericClass):
    def __init__(self, oid, session):
        super().__init__(oid, session)
        self.__payload = session.get('Grades', oid)['Grade']
        self.add_date = datetime.strptime(self.__payload['AddDate'], '%Y-%m-%d %H:%M:%S')
        self.grade = self.__payload['Grade']
        self.have_influence = self.__payload['IsConstituent']
        self.semester = self.__payload['Semester']

    @property
    def teacher(self):
        return SynergiaTeacher(self.__payload['AddedBy']['Id'], self._session)

    @property
    def subject(self):
        return SynergiaSubject(self.__payload['Subject']['Id'], self._session)

    @property
    def comments(self):
        grade_comments = []
        for c in self.__payload['Comments']:
            grade_comments.append(SynergiaGradeComment(c['Id'], self._session))
        return grade_comments


class SynergiaAttendanceType(SynergiaGenericClass):
    def __init__(self, oid, session):
        super().__init__(oid, session)
        self.__payload = session.get('Attendances', 'Types', oid)['Type']
        self.color = self.__payload['ColorRGB']
        self.is_presence_kind = self.__payload['IsPresenceKind']
        self.name = self.__payload['Name']


class SynergiaAttendance(SynergiaGenericClass):
    def __init__(self, oid, session):
        super().__init__(oid, session)
        self.__payload = session.get('Attendances', oid)['Attendance']
        self.add_date = datetime.strptime(self.__payload['AddDate'], '%Y-%m-%d %H:%M:%S')
        self.lesson_no = self.__payload['LessonNo']

    @property
    def teacher(self):
        return SynergiaTeacher(self.__payload['AddedBy']['Id'], self._session)

    @property
    def student(self):
        return SynergiaStudent(self.__payload['Student']['Id'], self._session)

    @property
    def type(self):
        return SynergiaAttendanceType(self.__payload['Type']['Id'], self._session)
