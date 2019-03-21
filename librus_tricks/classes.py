from datetime import datetime


def _try_to_extract(payload, extraction_key, false_return=None):
    if extraction_key in payload.keys():
        return payload[extraction_key]
    else:
        return false_return


class SynergiaGenericClass:
    def __init__(self, oid, session, resource, extraction_key, payload=None):
        self._session = session
        self.oid = int(oid)
        self.objects_ids = None
        if payload == None:
            self._json_payload = self._session.get(
                *resource,
                self.oid
            )[extraction_key]
        else:
            self._json_payload = payload

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.oid}>'


class SynergiaTeacher(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('Users',), 'User', payload)
        self.name = self._json_payload['FirstName']
        self.last_name = self._json_payload['LastName']


class SynergiaStudent(SynergiaTeacher):
    pass


class SynergiaGlobalClass(SynergiaGenericClass):
    """Klasa reprezentująca klasę (np. 1C)"""

    def __init__(self, oid, session, payload=None):
        """
        Tworzy obiekt reprezentujący klasę (jako zbiór uczniów)

        :param str oid: id klasy
        :param librus_tricks.core.SynergiaClient session: obiekt sesji z API Synergii
        :param dict payload: dane z json'a
        """
        super().__init__(oid, session, ('Classes',), 'Class', payload)

        class ObjectsIds:
            def __init__(self, id_tut):
                self.tutor = id_tut

        self.alias = f'{self._json_payload["Number"]}{self._json_payload["Symbol"]}'
        self.begin_date = datetime.strptime(self._json_payload['BeginSchoolYear'], '%Y-%m-%d')
        self.end_date = datetime.strptime(self._json_payload['EndSchoolYear'], '%Y-%m-%d')
        self.objects_ids = ObjectsIds(
            self._json_payload['ClassTutor']['Id']
        )

    @property
    def tutor(self):
        return SynergiaTeacher(self.objects_ids.tutor, self._session)

class SynergiaVirtualClass(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        """
        Tworzy obiekt reprezentujący grupę uczniów

        :param str oid: id klasy
        :param librus_tricks.core.SynergiaClient session: obiekt sesji z API Synergii
        :param dict payload: dane z json'a
        """
        super().__init__(oid, session, ('VirtualClasses',), 'VirtualClass', payload)

        class ObjectsIds:
            def __init__(self, id_sub, id_tea):
                self.subject = id_sub
                self.teacher = id_tea

        self.name = self._json_payload['Name']
        self.number = self._json_payload['Number']
        self.symbol = self._json_payload['Symbol']
        self.objects_ids = ObjectsIds(
            self._json_payload['Subject']['Id'],
            self._json_payload['Teacher']['Id']
        )

    @property
    def teacher(self):
        return SynergiaTeacher(self.objects_ids.teacher, self._session)

    @property
    def subject(self):
        return SynergiaSubject(self.objects_ids.subject, self._session)


class SynergiaSubject(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('Subjects',), 'Subject', payload)
        self.name = self._json_payload['Name']
        self.short_name = self._json_payload['Short']


class SynergiaLesson(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        """
        Klasa reprezentująca jednostkową lekcję

        :type session: librus_tricks.core.SynergiaClient
        """
        super().__init__(oid, session, ('Users',), 'User', payload)

        class ObjectsIds:
            def __init__(self, id_tea, id_grp, id_sub):
                self.teacher = id_tea
                self.group = id_grp
                self.subject = id_sub

        self.objects_ids = ObjectsIds(
            self._json_payload['Teacher']['Id'],
            self._json_payload['Class']['Id'],
            self._json_payload['Subject']['Id'],
        )

    @property
    def teacher(self):
        return SynergiaTeacher(self.objects_ids.teacher, self._session)

    @property
    def group(self):
        return SynergiaGlobalClass(self.objects_ids.group, self._session)

    @property
    def subject(self):
        return SynergiaSubject(self.objects_ids.subject, self._session)


class SynergiaGradeCategory(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('Grades', 'Categories',), 'Category', payload)

        class ObjectsIds:
            def __init__(self, id_tea):
                self.teacher = id_tea

        self.count_to_the_average = self._json_payload['CountToTheAverage']
        self.name = self._json_payload['Name']
        self.obligation_to_perform = self._json_payload['ObligationToPerform']
        self.standard = self._json_payload['Standard']
        self.weight = _try_to_extract(self._json_payload, 'Weight')
        self.objects_ids = ObjectsIds(
            _try_to_extract(self._json_payload, 'Teacher', {'Id': None})['Id']
        )

    @property
    def teacher(self):
        return SynergiaTeacher(self.objects_ids.teacher, self._session)


class SynergiaGradeComment(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('Grades', 'Comments',), 'Comment', payload)

        class ObjectsIds:
            def __init__(self, id_tea, id_grb):
                self.teacher = id_tea
                self.grade_bind = id_grb

        self.text = self._json_payload['Text']
        self.objects_ids = ObjectsIds(
            self._json_payload['AddedBy']['Id'],
            self._json_payload['Grade']['Id']
        )

    @property
    def teacher(self):
        return SynergiaTeacher(self.objects_ids, self._session)

    @property
    def grade_bind(self):
        return SynergiaGrade(self.objects_ids, self._session)


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

        class ObjectsIds:
            def __init__(self, id_tea, id_sub, ids_com, id_cat):
                self.teacher = id_tea
                self.subject = id_sub
                self.comments = ids_com
                self.category = id_cat

        self.add_date = datetime.strptime(self._json_payload['AddDate'], '%Y-%m-%d %H:%M:%S')
        self.date = datetime.strptime(self._json_payload['Date'], '%Y-%m-%d')
        self.grade = self._json_payload['Grade']
        self.is_constituent = self._json_payload['IsConstituent']
        self.semester = self._json_payload['Semester']
        self.metadata = GradeMetadata(
            self._json_payload['IsConstituent'],
            self._json_payload['IsSemester'],
            self._json_payload['IsSemesterProposition'],
            self._json_payload['IsFinal'],
            self._json_payload['IsFinalProposition']
        )
        self.objects_ids = ObjectsIds(
            self._json_payload['AddedBy']['Id'],
            self._json_payload['Subject']['Id'],
            [x['Id'] for x in _try_to_extract(self._json_payload, 'Comments', false_return=[])],
            self._json_payload['Category']['Id']
        )

    @property
    def teacher(self):
        return SynergiaTeacher(self.objects_ids.teacher, self._session)

    @property
    def subject(self):
        return SynergiaSubject(self.objects_ids.subject, self._session)

    @property
    def comments(self):
        if 'Comments' in self._json_payload.keys():
            return [SynergiaGradeComment(i, self._session) for i in self.objects_ids.comments]
        else:
            return []

    @property
    def category(self):
        return SynergiaGradeCategory(self.objects_ids.category, self._session)


class SynergiaAttendanceType(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('Attendances', 'Types',), 'Type', payload)
        self.color = self._json_payload['ColorRGB']
        self.is_presence_kind = self._json_payload['IsPresenceKind']
        self.name = self._json_payload['Name']
        self.short_name = self._json_payload['Short']

    def __repr__(self):
        return f'<SynergiaAttendanceType {self.short_name}>'


class SynergiaAttendance(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('Attendances',), 'Attendance', payload)

        class ObjectsIds:
            def __init__(self, id_tea, id_stu, id_typ):
                self.teacher = id_tea
                self.student = id_stu
                self.type = id_typ

        self.add_date = datetime.strptime(self._json_payload['AddDate'], '%Y-%m-%d %H:%M:%S')
        self.date = datetime.strptime(self._json_payload['Date'], '%Y-%m-%d')
        self.lesson_no = self._json_payload['LessonNo']
        self.objects_ids = ObjectsIds(
            self._json_payload['AddedBy']['Id'],
            self._json_payload['Student']['Id'],
            self._json_payload['Type']['Id']
        )

    @property
    def teacher(self):
        return SynergiaTeacher(self.objects_ids.teacher, self._session)

    @property
    def student(self):
        return SynergiaStudent(self.objects_ids.student, self._session)

    @property
    def type(self):
        return SynergiaAttendanceType(self.objects_ids.type, self._session)

    def __repr__(self):
        return f'<SynergiaAttendance at {self.add_date}>'


class SynergiaExamCategory(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('HomeWorks', 'Categories'), 'Category', payload)

        class ObjectsIds:
            def __init__(self, id_col):
                self.color = id_col

        self.name = self._json_payload['Name']
        self.objects_ids = ObjectsIds(self._json_payload['Color']['Id'])

    @property
    def color(self):
        return SynergiaColor(self.objects_ids.color, self._session)


class SynergiaExam(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('HomeWorks',), 'HomeWork', payload)

        def _define_group_and_type(payload):
            """

            :param dict payload:
            :return:
            """
            if 'VirtualClass' in payload.keys():
                return {'Id': payload['VirtualClass']['Id'], 'type': SynergiaVirtualClass}
            elif 'Class' in payload.keys():
                return {'Id': payload['Class']['Id'], 'type': SynergiaGlobalClass}
            else:
                raise AttributeError('Wrong object type')

        class ObjectsIds:
            def __init__(self, id_tea, id_cls, id_cat, id_sub):
                self.teacher = id_tea
                self.group = id_cls
                self.category = id_cat
                self.subject = id_sub

        self.add_date = datetime.strptime(self._json_payload['AddDate'], '%Y-%m-%d %H:%M:%S')
        self.content = self._json_payload['Content']
        self.date = datetime.strptime(self._json_payload['Date'], '%Y-%m-%d')
        self.lesson = self._json_payload['LessonNo']
        self.time_start = self._json_payload['TimeFrom']
        self.time_end = self._json_payload['TimeTo']
        self.objects_ids = ObjectsIds(
            self._json_payload['CreatedBy']['Id'],
            _define_group_and_type(self._json_payload),
            self._json_payload['Category']['Id'],
            _try_to_extract(self._json_payload, 'Subject', {'Id': None})['Id']
        )

    @property
    def teacher(self):
        return SynergiaTeacher(self.objects_ids.teacher, self._session)

    @property
    def group(self):
        return SynergiaGlobalClass(self.objects_ids.group, self._session)

    @property
    def subject(self):
        return SynergiaSubject(self.objects_ids.subject, self._session)


class SynergiaColor(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('Colors',), 'Color', payload)
        self.name = self._json_payload['Name']
        self.hex_rgb = self._json_payload['RGB']
