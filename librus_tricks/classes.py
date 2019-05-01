from datetime import datetime


def _try_to_extract(payload, extraction_key, false_return=None):
    if extraction_key in payload.keys():
        return payload[extraction_key]
    else:
        return false_return


class SynergiaGenericClass:
    def __init__(self, oid, session, resource, extraction_key, payload=None):
        """

        :param str oid: Id żądanego obiektu
        :param session:
        :param resource:
        :type resource: tuple of str
        :param str extraction_key:
        :param dict payload:
        """
        self._session = session
        self.oid = int(oid)
        self.objects_ids = None
        if payload is None:
            self._json_payload = self._session.get(
                *resource,
                self.oid
            )[extraction_key]
        else:
            self._json_payload = payload

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.oid} at {hex(id(self))}>'


class SynergiaTeacher(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('Users',), 'User', payload)
        self.name = self._json_payload['FirstName']
        self.last_name = self._json_payload['LastName']

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name} {self.last_name}>'

    def __str__(self):
        return f'{self.name} {self.last_name}'


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
        self.begin_date = datetime.strptime(self._json_payload['BeginSchoolYear'], '%Y-%m-%d').date()
        self.end_date = datetime.strptime(self._json_payload['EndSchoolYear'], '%Y-%m-%d').date()
        self.objects_ids = ObjectsIds(
            self._json_payload['ClassTutor']['Id']
        )

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.alias}>'

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

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name}>'

    @property
    def teacher(self):
        """

        :rtype: SynergiaTeacher
        """
        return self._session.csync(self.objects_ids.teacher, SynergiaTeacher)

    @property
    def subject(self):
        """

        :rtype: SynergiaSubject
        """
        return self._session.csync(self.objects_ids.subject, SynergiaSubject)


class SynergiaSubject(SynergiaGenericClass):

    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('Subjects',), 'Subject', payload)
        self.name = self._json_payload['Name']
        self.short_name = self._json_payload['Short']

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name}>'


class SynergiaLesson(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        """
        Klasa reprezentująca jednostkową lekcję

        :type session: librus_tricks.core.SynergiaClient
        """
        super().__init__(oid, session, ('Lessons',), 'Lesson', payload)

        class ObjectsIds:
            def __init__(self, id_tea, id_grp, id_sub):
                self.teacher = id_tea
                self.group = id_grp
                self.subject = id_sub

        if 'Class' not in self._json_payload.keys():
            self._json_payload['Class'] = {}
            self._json_payload['Class']['Id'] = None

        self.objects_ids = ObjectsIds(
            self._json_payload['Teacher']['Id'],
            self._json_payload['Class']['Id'],
            self._json_payload['Subject']['Id'],
        )

    @property
    def teacher(self):
        """

        :rtype: SynergiaTeacher
        """
        return self._session.csync(self.objects_ids.teacher, SynergiaTeacher)

    @property
    def group(self):

        if self.objects_ids.group is None:
            return None
        else:
            return SynergiaGlobalClass(self.objects_ids.group, self._session)

    @property
    def subject(self):

        return self._session.csync(self.objects_ids.subject, SynergiaSubject)


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
        self.weight = _try_to_extract(self._json_payload, 'Weight', false_return=0)
        self.objects_ids = ObjectsIds(
            _try_to_extract(self._json_payload, 'Teacher', {'Id': None})['Id']
        )

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name}>'

    @property
    def teacher(self):
        """

        :rtype: SynergiaTeacher
        """
        return self._session.csync(self.objects_ids.teacher, SynergiaTeacher)


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

    def __str__(self):
        return self.text

    @property
    def teacher(self):
        """

        :rtype: SynergiaTeacher
        """
        return self._session.csync(self.objects_ids.teacher, SynergiaTeacher)

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
        self.date = datetime.strptime(self._json_payload['Date'], '%Y-%m-%d').date()
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

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.grade} from SynergiaSubject with id {self.objects_ids.subject} ' \
            f'added {self.add_date.strftime("%Y-%m-%d %H:%M:%S")}>'

    def __str__(self):
        return self.grade

    @property
    def teacher(self):
        """

        :rtype: SynergiaTeacher
        """
        return self._session.csync(self.objects_ids.teacher, SynergiaTeacher)

    @property
    def subject(self):
        """

        :rtype: SynergiaSubject
        """
        return self._session.csync(self.objects_ids.subject, SynergiaSubject)

    @property
    def comments(self):
        """

        :rtype: list of SynergiaGradeComment
        """
        if 'Comments' in self._json_payload.keys():
            return [self._session.csync(i, SynergiaGradeComment) for i in self.objects_ids.comments]
        else:
            return []

    @property
    def category(self):
        """

        :rtype: SynergiaGradeCategory
        """
        return self._session.csync(self.objects_ids.category, SynergiaGradeCategory)

    @property
    def real_value(self):
        try:
            return {
                '1': 1,
                '1+': 1.25,
                '2-': 1.75,
                '2': 2,
                '2+': 2.25,
                '3-': 2.75,
                '3': 3,
                '3+': 3.25,
                '4-': 4.75,
                '4': 4,
                '4+': 4.25,
                '5-': 4.75,
                '5': 5,
                '5+': 5.25,
                '6-': 5.75,
                '6': 6
            }[self.grade]
        except KeyError:
            return None


class SynergiaAttendanceType(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('Attendances', 'Types',), 'Type', payload)
        self.color = self._json_payload['ColorRGB']
        self.is_presence_kind = self._json_payload['IsPresenceKind']
        self.name = self._json_payload['Name']
        self.short_name = self._json_payload['Short']

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.short_name}>'


class SynergiaAttendance(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('Attendances',), 'Attendance', payload)

        class ObjectsIds:
            def __init__(self, id_tea, id_stu, id_typ):
                self.teacher = id_tea
                self.student = id_stu
                self.type = id_typ

        self.add_date = datetime.strptime(self._json_payload['AddDate'], '%Y-%m-%d %H:%M:%S')
        self.date = datetime.strptime(self._json_payload['Date'], '%Y-%m-%d').date()
        self.lesson_no = self._json_payload['LessonNo']
        self.objects_ids = ObjectsIds(
            self._json_payload['AddedBy']['Id'],
            self._json_payload['Student']['Id'],
            self._json_payload['Type']['Id']
        )

    @property
    def teacher(self):
        """

        :rtype: SynergiaTeacher
        """
        return self._session.csync(self.objects_ids.teacher, SynergiaTeacher)

    @property
    def student(self):
        """

        :rtype: SynergiaStudent
        """
        return self._session.csync(self.objects_ids.student, SynergiaStudent)

    @property
    def type(self):
        """

        :rtype: SynergiaAttendanceType
        """
        return self._session.csync(self.objects_ids.type, SynergiaAttendanceType)

    def __repr__(self):
        return f'<SynergiaAttendance at {self.add_date.strftime("%Y-%m-%d %H:%M:%S")} ({self.oid})>'

    def __str__(self):
        return self.type


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
        return self._session.csync(self.objects_ids.color, SynergiaColor)


class SynergiaExam(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):

        super().__init__(oid, session, ('HomeWorks',), 'HomeWork', payload)

        def _define_group_and_type(exam_payload):
            """

            :param dict exam_payload:
            :return:
            """
            if 'VirtualClass' in exam_payload.keys():
                return {'Id': exam_payload['VirtualClass']['Id'], 'type': SynergiaVirtualClass}
            elif 'Class' in exam_payload.keys():
                return {'Id': exam_payload['Class']['Id'], 'type': SynergiaGlobalClass}
            else:
                raise AttributeError('Wrong object type')

        class ObjectsIds:
            def __init__(self, id_tea, group_id, group_type, id_cat, id_sub):
                self.teacher = id_tea
                self.group = group_id
                self.group_type = group_type
                self.category = id_cat
                self.subject = id_sub

        self.add_date = datetime.strptime(self._json_payload['AddDate'], '%Y-%m-%d %H:%M:%S')
        self.content = self._json_payload['Content']
        self.date = datetime.strptime(self._json_payload['Date'], '%Y-%m-%d').date()
        self.lesson = self._json_payload['LessonNo']
        if self._json_payload['TimeFrom'] is None:
            self.time_start = None
        else:
            self.time_start = datetime.strptime(self._json_payload['TimeFrom'], '%H:%M:%S').time()
        if self._json_payload['TimeTo'] is None:
            self.time_end = None
        else:
            self.time_end = datetime.strptime(self._json_payload['TimeTo'], '%H:%M:%S').time()
        self.objects_ids = ObjectsIds(
            self._json_payload['CreatedBy']['Id'],
            _define_group_and_type(self._json_payload)['Id'],
            _define_group_and_type(self._json_payload)['type'],
            self._json_payload['Category']['Id'],
            _try_to_extract(self._json_payload, 'Subject', {'Id': None})['Id']
        )

    def __repr__(self):
        return f'<{self.__class__.__name__} ' \
            f'{self.date.strftime("%Y-%m-%d")} for subject with id {self.objects_ids.subject}>'

    @property
    def teacher(self):
        """

        :rtype: SynergiaTeacher
        """
        return self._session.csync(self.objects_ids.teacher, SynergiaTeacher)

    @property
    def group(self):
        """

        :rtype: SynergiaGlobalClass
        :rtype: SynergiaVirtualClass
        """
        if self.objects_ids.group_type is SynergiaGlobalClass:
            return SynergiaGlobalClass(self.objects_ids.group, self._session)
        else:
            return SynergiaVirtualClass(self.objects_ids.group, self._session)

    @property
    def subject(self):
        """

        :rtype: SynergiaSubject
        """
        if self.objects_ids.subject is None:
            class FakeSynergiaSubject:
                def __init__(self):
                    self.name = 'Przedmiot nie określony'
                    self.short_name = None
            return FakeSynergiaSubject()
        else:
            return self._session.csync(self.objects_ids.subject, SynergiaSubject)

    @property
    def category(self):
        """

        :rtype: SynergiaExamCategory
        """
        return self._session.csync(self.objects_ids.category, SynergiaExamCategory)


class SynergiaColor(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('Colors',), 'Color', payload)
        self.name = self._json_payload['Name']
        self.hex_rgb = self._json_payload['RGB']

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.hex_rgb}>'

    def __str__(self):
        return self.hex_rgb


class SynergiaClassroom(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('Classrooms',), 'Classroom', payload)
        self.name = self._json_payload['Name']
        self.symbol = self._json_payload['Symbol']


class SynergiaTeacherFreeDaysTypes(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('TeacherFreeDays', 'Types'), 'Types', payload)
        self.name = self._json_payload[0]['Name']


class SynergiaTeacherFreeDays(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None):
        super().__init__(oid, session, ('TeacherFreeDays',), 'TeacherFreeDay', payload)

        class ObjectsIds:
            def __init__(self, tea_id, type_id):
                self.teacher = tea_id
                self.type = type_id

        self.starts = datetime.strptime(self._json_payload['DateFrom'], '%Y-%m-%d').date()
        self.ends = datetime.strptime(self._json_payload['DateTo'], '%Y-%m-%d').date()
        self.objects_ids = ObjectsIds(
            self._json_payload['Teacher']['Id'],
            self._json_payload['Type']['Id']
        )

    # TODO: Dodać __repr__()

    @property
    def teacher(self):
        return self._session.csync(self.objects_ids.teacher, SynergiaTeacher)

    @property
    def type(self):
        return self._session.csync(self.objects_ids.type, SynergiaTeacherFreeDaysTypes)


class SynergiaSchoolFreeDays(SynergiaGenericClass):
    def __init__(self, oid, session, payload=None, from_origin=False):
        super().__init__(oid, session, ('SchoolFreeDays',), 'SchoolFreeDays', payload)
        if from_origin:
            self._json_payload = self._json_payload[0]
        self.starts = datetime.strptime(self._json_payload['DateFrom'], '%Y-%m-%d').date()
        self.ends = datetime.strptime(self._json_payload['DateTo'], '%Y-%m-%d').date()
        self.name = self._json_payload['Name']  # TODO: Dodać Units
    # TODO: Wymagany debug oraz test

    # TODO: Dodać __repr__()
