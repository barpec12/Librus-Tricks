from datetime import datetime, date, time


def _try_to_extract(payload, extraction_key, false_return=None):
    if extraction_key in payload.keys():
        return payload[extraction_key]
    else:
        return false_return


class _RemoteObjectsUIDManager:
    def __init__(self, session, parent):
        """

        :param librus_tricks.core.SynergiaClient session:
        """
        self.__storage = dict()
        self._session = session
        self.__parent = parent

    def set_object(self, attr, uid, cls):
        self.__storage[attr] = uid, cls
        # self.__parent.__setattr__(attr, cls.create(uid=uid, session=self.__session))
        return self

    def assembly(self, attr):
        uid, cls = self.__storage[attr]
        return cls.create(uid=uid, session=self._session)

    def return_id(self, attr):
        return self.__storage[attr][0]


class SynergiaGenericClass:
    def __init__(self, uid, resource, session):
        """

        :param str uid: Id żądanego obiektu
        :param librus_tricks.core.SynergiaClient session: Obiekt sesji
        :param resource: ścieżka do źródła danych
        :type resource: iterable of str
        :param str extraction_key: str zawierający klucz do wyjęcia danych
        :param dict resource: dict zawierający gotowe dane (np. załadowane z cache)
        """

        self._session = session
        self.uid = uid
        self.objects = _RemoteObjectsUIDManager(self._session, self)
        self._json_resource = resource

    # Of course i can comment it out, but for code completion props will be better
    # def __getattr__(self, name):
    #     return self.objects_ids.assembly(name)

    @classmethod
    def assembly(cls, resource, session):
        self = cls(resource['Id'], resource, session)
        return self

    @classmethod
    def create(cls, uid=None, path=('',), session=None, extraction_key=None):
        """

        :param uid:
        :param path:
        :param librus_tricks.core.SynergiaClient session:
        :param extraction_key:
        :return:
        """
        if uid is None or session is None:
            raise Exception()  # TODO: specify exception

        response = session.get_cached_response(*path, uid)

        if extraction_key is None:
            extraction_key = SynergiaGenericClass.auto_extract(response)

        resource = response[extraction_key]
        self = cls(resource['Id'], resource, session)
        return self

    @staticmethod
    def auto_extract(payload):
        for key in payload.keys():
            if key not in ('Resources', 'Url'):
                return key

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.uid} at {hex(id(self))}>'


class SynergiaTeacher(SynergiaGenericClass):
    def __init__(self, uid, resource, session):
        super().__init__(uid, resource, session)
        self.name = self._json_resource['FirstName']
        self.last_name = self._json_resource['LastName']

    @classmethod
    def create(cls, uid=None, path=('Users',), session=None, extraction_key='User'):
        self = super().create(uid, path, session, extraction_key)
        return self

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name} {self.last_name}>'

    def __str__(self):
        return f'{self.name} {self.last_name}'


class SynergiaStudent(SynergiaTeacher):
    pass


class SynergiaGlobalClass(SynergiaGenericClass):
    """Klasa reprezentująca klasę (np. 1C)"""

    def __init__(self, uid, resource, session):
        """
        Tworzy obiekt reprezentujący klasę (jako zbiór uczniów)

        :param str uid: id klasy
        :param librus_tricks.core.SynergiaClient session: obiekt sesji z API Synergii
        :param dict resource: dane z json'a
        """
        super().__init__(uid, resource, session)

        self.alias = f'{self._json_resource["Number"]}{self._json_resource["Symbol"]}'
        self.begin_date = datetime.strptime(self._json_resource['BeginSchoolYear'], '%Y-%m-%d').date()
        self.end_date = datetime.strptime(self._json_resource['EndSchoolYear'], '%Y-%m-%d').date()
        self.objects.set_object(
            'tutor', self._json_resource['ClassTutor']['Id'], SynergiaTeacher
        )

    @property
    def tutor(self) -> SynergiaTeacher:
        return self.objects.assembly('tutor')

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.alias}>'


class SynergiaVirtualClass(SynergiaGenericClass):
    def __init__(self, uid, resource, session):
        """
        Tworzy obiekt reprezentujący grupę uczniów

        :param str uid: id klasy
        :param librus_tricks.core.SynergiaClient session: obiekt sesji z API Synergii
        :param dict resource: dane z json'a
        """
        super().__init__(uid, resource, session)

        self.name = self._json_resource['Name']
        self.number = self._json_resource['Number']
        self.symbol = self._json_resource['Symbol']
        self.objects.set_object(
            'teacher', self._json_resource['Teacher']['Id'], SynergiaTeacher
        ).set_object(
            'subject', self._json_resource['Subject']['Id'], SynergiaSubject
        )

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name}>'

    @property
    def teacher(self) -> SynergiaTeacher:
        return self.objects.assembly('teacher')

    @property
    def subject(self):
        return self.objects.assembly('subject')


class SynergiaSubject(SynergiaGenericClass):
    def __init__(self, uid, resource, session):
        super().__init__(uid, resource, session)
        self.name = self._json_resource['Name']
        self.short_name = self._json_resource['Short']

    @classmethod
    def create(cls, uid=None, path=('Subjects',), session=None, extraction_key='Subject'):
        self = super().create(uid, path, session, extraction_key)
        return self

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name}>'

    def __str__(self):
        return self.name


class SynergiaLesson(SynergiaGenericClass):
    def __init__(self, uid, resource, session):
        """
        Klasa reprezentująca jednostkową lekcję

        :type session: librus_tricks.core.SynergiaClient
        """
        super().__init__(uid, resource, session)

        if 'Class' in self._json_resource.keys():
            self.objects.set_object('group', self._json_resource['Class']['Id'], SynergiaGlobalClass)

        self.objects.set_object(
            'teacher', self._json_resource['Teacher']['Id'], SynergiaTeacher
        ).set_object(
            'subject', self._json_resource['Subject']['Id'], SynergiaSubject
        )

    @classmethod
    def create(cls, uid=None, path=('Lessons',), session=None, extraction_key='Lesson'):
        self = super().create(uid, path, session, extraction_key)
        return self

    @property
    def teacher(self) -> SynergiaTeacher:
        return self.objects.assembly('teacher')

    @property
    def subject(self) -> SynergiaSubject:
        return self.objects.assembly('subject')


class SynergiaGradeCategory(SynergiaGenericClass):
    def __init__(self, uid, resource, session):
        super().__init__(uid, resource, session)
        self.count_to_the_average = self._json_resource['CountToTheAverage']
        self.name = self._json_resource['Name']
        self.obligation_to_perform = self._json_resource['ObligationToPerform']
        self.standard = self._json_resource['Standard']
        self.weight = _try_to_extract(self._json_resource, 'Weight', false_return=0)

        if 'Teacher' in self._json_resource.keys():
            self.objects.set_object(
                'teacher', self._json_resource['Id'], SynergiaTeacher
            )

    @classmethod
    def create(cls, uid=None, path=('Grades', 'Categories'), session=None, extraction_key='Category'):
        self = super().create(uid, path, session, extraction_key)
        return self

    @property
    def teacher(self) -> SynergiaTeacher:
        return self.objects.assembly('teacher')

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name}>'


class SynergiaGradeComment(SynergiaGenericClass):
    def __init__(self, uid, resource, session):
        super().__init__(uid, resource, session)

        self.text = self._json_resource['Text']
        self.objects.set_object(
            'teacher', self._json_resource['AddedBy']['Id'], SynergiaTeacher
        ).set_object(
            'bind', self._json_resource['Grade']['Id'], SynergiaGrade
        )

    def __str__(self):
        return self.text

    @property
    def teacher(self) -> SynergiaTeacher:
        return self.objects.assembly('teacher')

    @property
    def grade_bind(self):
        return self.objects.assembly('bind')


class SynergiaBaseTextGrade(SynergiaGenericClass):
    def __init__(self, uid, resource, session):
        super().__init__(uid, resource, session)

        self.add_date = datetime.strptime(self._json_resource['AddDate'], '%Y-%m-%d %H:%M:%S')
        self.date = datetime.strptime(self._json_resource['Date'], '%Y-%m-%d').date()
        self.grade = self._json_resource['Grade']
        self.semester = self._json_resource['Semester']
        self.visible = self._json_resource['ShowInGradesView']
        self.objects.set_object(
            'teacher', self._json_resource['AddedBy']['Id'], SynergiaTeacher
        ).set_object(
            'subject', self._json_resource['Subject']['Id'], SynergiaSubject
        ).set_object(
            'student', self._json_resource['Student']['Id'], SynergiaStudent
        )

    @classmethod
    def create(cls, uid=None, path=('BaseTextGrades',), session=None, extraction_key='BaseTextGrades'):
        self = super().create(uid, path, session, extraction_key)
        return self

    @property
    def teacher(self) -> SynergiaTeacher:
        return self.objects.assembly('teacher')

    # TODO: add category prop
    # TODO: add lesson prop

    @property
    def subject(self) -> SynergiaSubject:
        return self.objects.assembly('subject')

    @property
    def student(self):
        return self.objects.assembly('student')


class SynergiaGrade(SynergiaGenericClass):
    def __init__(self, uid, resource, session):
        super().__init__(uid, resource, session)

        class GradeMetadata:
            def __init__(self, is_c, is_s, is_sp, is_f, is_fp):
                self.is_constituent = is_c
                self.is_semester_grade = is_s
                self.is_semester_grade_proposition = is_sp
                self.is_final_grade = is_f
                self.is_final_grade_proposition = is_fp

        self.add_date = datetime.strptime(self._json_resource['AddDate'], '%Y-%m-%d %H:%M:%S')
        self.date = datetime.strptime(self._json_resource['Date'], '%Y-%m-%d').date()
        self.grade = self._json_resource['Grade']
        self.is_constituent = self._json_resource['IsConstituent']
        self.semester = self._json_resource['Semester']
        self.metadata = GradeMetadata(
            self._json_resource['IsConstituent'],
            self._json_resource['IsSemester'],
            self._json_resource['IsSemesterProposition'],
            self._json_resource['IsFinal'],
            self._json_resource['IsFinalProposition']
        )

        self.objects.set_object(
            'teacher', self._json_resource['AddedBy']['Id'], SynergiaTeacher
        ).set_object(
            'subject', self._json_resource['Subject']['Id'], SynergiaSubject
        ).set_object(
            'category', self._json_resource['Category']['Id'], SynergiaGradeCategory
        )

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.grade} from SynergiaSubject with id {self.objects.return_id("subject")} ' \
               f'added {self.add_date.strftime("%Y-%m-%d %H:%M:%S")}>'

    def __str__(self):
        return self.grade

    @property
    def teacher(self) -> SynergiaTeacher:
        return self.objects.assembly('teacher')

    @property
    def subject(self) -> SynergiaSubject:
        return self.objects.assembly('subject')

    @property
    def category(self) -> SynergiaGradeCategory:
        return self.objects.assembly('category')

    @property
    def comments(self):
        """

        :rtype: list of SynergiaGradeComment
        """
        if 'Comments' in self._json_resource.keys():
            return [SynergiaGradeComment.create(i["Id"], self._session) for i in
                    _try_to_extract(self._json_resource, 'Comments', false_return=[])]
        else:
            return []

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
    def __init__(self, uid, resource, session):
        super().__init__(uid, resource, session)
        self.color = self._json_resource['ColorRGB']
        self.is_presence_kind = self._json_resource['IsPresenceKind']
        self.name = self._json_resource['Name']
        self.short_name = self._json_resource['Short']

    @classmethod
    def create(cls, uid=None, path=('Attendances', 'Types'), session=None, extraction_key='Type'):
        self = super().create(uid, path, session, extraction_key)
        return self

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.short_name}>'


class SynergiaAttendance(SynergiaGenericClass):
    def __init__(self, uid, resource, session):
        super().__init__(uid, resource, session)
        self.add_date = datetime.strptime(self._json_resource['AddDate'], '%Y-%m-%d %H:%M:%S')
        self.date = datetime.strptime(self._json_resource['Date'], '%Y-%m-%d').date()
        self.lesson_no = self._json_resource['LessonNo']
        self.objects.set_object(
            'teacher', self._json_resource['AddedBy']['Id'], SynergiaTeacher
        ).set_object(
            'student', self._json_resource['Student']['Id'], SynergiaStudent
        ).set_object(
            'type', self._json_resource['Type']['Id'], SynergiaAttendanceType
        )

    @classmethod
    def create(cls, uid=None, path=('Attendances',), session=None, extraction_key='Attendance'):
        self = super().create(uid, path, session, extraction_key)
        return self

    @property
    def teacher(self) -> SynergiaTeacher:
        return self.objects.assembly('teacher')

    @property
    def student(self):
        return self.objects.assembly('student')

    @property
    def type(self):
        return self.objects.assembly('type')

    def __repr__(self):
        return f'<SynergiaAttendance at {self.add_date.strftime("%Y-%m-%d %H:%M:%S")} ({self.uid})>'

    def __str__(self):
        return self.type


class SynergiaExamCategory(SynergiaGenericClass):
    def __init__(self, uid, resource, session):
        super().__init__(uid, resource, session)

        self.name = self._json_resource['Name']
        self.objects.set_object('color', self._json_resource['Color']['Id'], SynergiaColor)

    @classmethod
    def create(cls, uid=None, path=('HomeWorks', 'Categories'), session=None, extraction_key='Category'):
        self = super().create(uid, path, session, extraction_key)
        return self

    @property
    def color(self):
        """

        :rtype: SynergiaColor
        """
        return self.objects.assembly('color')

    def __str__(self):
        return self.name


class SynergiaExam(SynergiaGenericClass):
    def __init__(self, uid, resource, session):

        super().__init__(uid, resource, session)

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

        self.add_date = datetime.strptime(self._json_resource['AddDate'], '%Y-%m-%d %H:%M:%S')
        self.content = self._json_resource['Content']
        self.date = datetime.strptime(self._json_resource['Date'], '%Y-%m-%d').date()
        self.lesson = self._json_resource['LessonNo']
        if self._json_resource['TimeFrom'] is None:
            self.time_start = None
        else:
            self.time_start = datetime.strptime(self._json_resource['TimeFrom'], '%H:%M:%S').time()
        if self._json_resource['TimeTo'] is None:
            self.time_end = None
        else:
            self.time_end = datetime.strptime(self._json_resource['TimeTo'], '%H:%M:%S').time()

        self.objects.set_object(
            'teacher', self._json_resource['CreatedBy']['Id'], SynergiaTeacher
        ).set_object(
            'category', self._json_resource['Category']['Id'], SynergiaExamCategory
        )
        if 'Subject' in self._json_resource:
            self.objects.set_object('subject', self._json_resource['Subject']['Id'], SynergiaSubject)
            self.__subject_present = True
        else:
            self.__subject_present = False

    @classmethod
    def create(cls, uid=None, path=('HomeWorks',), session=None, extraction_key='HomeWork'):
        self = super().create(uid, path, session, extraction_key)
        return self

    def __repr__(self):
        return f'<{self.__class__.__name__} ' \
               f'{self.date.strftime("%Y-%m-%d")} for subject {self.subject}>'

    @property
    def teacher(self) -> SynergiaTeacher:
        return self.objects.assembly('teacher')

    # @property
    # def group(self):
    #    """
    #
    #    :rtype: SynergiaGlobalClass
    #    :rtype: SynergiaVirtualClass
    #    """
    #    if self.objects_ids.group_type is SynergiaGlobalClass:
    #        return SynergiaGlobalClass(self.objects_ids.group, self._session)
    #    else:
    #        return SynergiaVirtualClass(self.objects_ids.group, self._session)

    @property
    def subject(self) -> SynergiaSubject:
        if self.__subject_present:
            return self.objects.assembly('subject')
        else:
            return None

    @property
    def category(self):
        return self.objects.assembly('category')


class SynergiaColor(SynergiaGenericClass):
    def __init__(self, uid, resource, session):
        super().__init__(uid, resource, session)
        self.name = self._json_resource['Name']
        self.hex_rgb = self._json_resource['RGB']

    @classmethod
    def create(cls, uid=None, path=('Colors',), session=None, extraction_key='Color'):
        self = super().create(uid, path, session, extraction_key)
        return self

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.hex_rgb}>'

    def __str__(self):
        return self.hex_rgb


class SynergiaClassroom(SynergiaGenericClass):
    def __init__(self, uid, resource, session):
        super().__init__(uid, resource, session)
        self.name = self._json_resource['Name']
        self.symbol = self._json_resource['Symbol']

    def __repr__(self):
        return f'<SynergiaClassroom {self.symbol}>'

    def __str__(self):
        return self.name


class SynergiaTeacherFreeDaysTypes(SynergiaGenericClass):
    def __init__(self, uid, resource, session):
        super().__init__(uid, resource, session)
        self.name = self._json_resource[0]['Name']


class SynergiaTeacherFreeDays(SynergiaGenericClass):
    def __init__(self, uid, resource, session):
        super().__init__(uid, resource, session)

        self.starts = datetime.strptime(self._json_resource['DateFrom'], '%Y-%m-%d').date()
        self.ends = datetime.strptime(self._json_resource['DateTo'], '%Y-%m-%d').date()
        self.objects.set_object(
            'teacher', self._json_resource['Teacher']['Id'], SynergiaTeacher
        ).set_object(
            'type', self._json_resource['Type']['Id'], SynergiaTeacherFreeDaysTypes
        )

    @property
    def teacher(self) -> SynergiaTeacher:
        """

        :rtype: SynergiaTeacher
        """
        return self.objects.assembly('teacher')

    @property
    def type(self):
        """

        :rtype: SynergiaTeacherFreeDaysTypes
        """
        return self.objects.assembly('type')

    def __repr__(self):
        return f'<SynergiaTeacherFreeDays {self.starts.isoformat()}-{self.ends.isoformat()} for {self.teacher.__repr__()}>'


class SynergiaSchoolFreeDays(SynergiaGenericClass):
    def __init__(self, uid, resource, session, from_origin=False):
        super().__init__(uid, resource, session)
        if from_origin:
            self._json_payload = self._json_payload[0]
        self.starts = datetime.strptime(self._json_payload['DateFrom'], '%Y-%m-%d').date()
        self.ends = datetime.strptime(self._json_payload['DateTo'], '%Y-%m-%d').date()
        self.name = self._json_payload['Name']  # TODO: Dodać Units

    @classmethod
    def create(cls, uid=None, path=('',), session=None, extraction_key=None):
        self = super().create(uid, path, session, extraction_key)
        return self
    # TODO: Wymagany debug oraz test

    # TODO: Dodać __repr__()


class SynergiaSchool(SynergiaGenericClass):
    def __init__(self, uid, resource, session):
        super().__init__(uid, resource, session)
        self.name = self._json_resource['Name']
        self.school_location = {
            'street': self._json_resource['Street'],
            'street_no': self._json_resource['BuildingNumber'],
            'state': self._json_resource['State'],
            'town': self._json_resource['Town']
        }

    def __repr__(self):
        return f'<SynergiaSchool {self.name}>'

    def __str__(self):
        return self.name


class SynergiaTimetableEntry(SynergiaGenericClass):
    def __init__(self, uid, resource, session):
        super().__init__(uid, resource, session)
        self.available = datetime.fromisoformat(resource['DateFrom']).date(), \
                         datetime.fromisoformat(resource['DateTo']).date()

    @classmethod
    def create(cls, uid=None, path=('TimetableEntries',), session=None, extraction_key='TimetableEntry'):
        self = super().create(uid, path, session, extraction_key)
        return self


class SynergiaTimetableEvent:
    def __init__(self, resource, session):
        self.lesson_no = resource['LessonNo']
        self.start = time.fromisoformat(resource['HourFrom'])
        self.end = time.fromisoformat(resource['HourTo'])
        self.is_cancelled = resource['IsCanceled']
        self.is_sub = resource['IsSubstitutionClass']
        self.preloaded = {
            'subject_title': resource['Subject']['Name'],
            'teacher': f'{resource["Teacher"]["FirstName"]} {resource["Teacher"]["LastName"]}'
        }
        self.objects = _RemoteObjectsUIDManager(session, self)
        self.objects.set_object(
            'subject', resource['Subject']['Id'], SynergiaSubject
        ).set_object(
            'teacher', resource['Teacher']['Id'], SynergiaTeacher
        )

    @property
    def subject(self):
        return self.objects.assembly('subject')

    def __repr__(self):
        return f'<SynergiaTimetableEvent {self.preloaded["subject_title"]} {self.start} {self.end} with {self.preloaded["teacher"]}>'

    def __str__(self):
        return self.preloaded["subject_title"]


class SynergiaTimetable(SynergiaGenericClass):
    def __init__(self, uid, resource, session):
        super().__init__(uid, resource, session)
        self.lessons = self.convert_parsed_timetable(
            self.parse_timetable(resource)
        )

    @property
    def today_timetable(self):
        """

        :rtype: list of SynergiaTimetableEvent
        """
        return self.lessons[datetime.now().date()]

    @classmethod
    def assembly(cls, resource, session):
        pseudo_id = int(datetime.now().timestamp()).__str__()
        self = cls(pseudo_id, resource, session)
        return self

    @classmethod
    def create(cls, uid=None, path=('Timetables',), session=None, extraction_key='Timetable', week=None):
        response = session.get_cached_response(*path)

        if extraction_key is None:
            extraction_key = SynergiaGenericClass.auto_extract(response)

        resource = response[extraction_key]
        self = cls.assembly(resource, session)
        return self

    @staticmethod
    def parse_timetable(resource):
        root = {}

        for day in resource.keys():
            day_date = date.fromisoformat(day)
            root[day_date] = []
            for period in resource[day]:
                if period.__len__() != 0:
                    root[day_date].append(period[0])
                else:
                    root[day_date].append({})
        return root

    def convert_parsed_timetable(self, timetable):
        for day in timetable:
            for event_index in range(len(timetable[day])):
                if timetable[day][event_index].keys().__len__() != 0:
                    timetable[day][event_index] = SynergiaTimetableEvent(timetable[day][event_index], self._session)
        return timetable

    def __repr__(self):
        return f'<{self.__class__.__name__} for {self.lessons.keys()}>'

    def __str__(self):
        o_str = ''
        for d in self.lessons.keys():
            o_str += f'{d}\n'
            for e in self.lessons[d]:
                if e != {}:
                    o_str += f'  {e.__str__()}\n'
        return o_str



class SynergiaNativeMessage(SynergiaGenericClass):
    def __init__(self, uid, resource, session):
        super().__init__(uid, resource, session)
        self.body = self._json_resource['Body']
        self.topic = self._json_resource['Subject']
        self.send_date = datetime.fromtimestamp(self._json_resource['SendDate'])
        # self.objects.set_object('sender', self._json_resource['Sender']['Id'], SynergiaTeacher)

    # @property
    # def sender(self) -> SynergiaTeacher:
    #     return self.objects.assembly('sender')

    @classmethod
    def create(cls, uid=None, path=('Messages',), session=None, extraction_key='Message'):
        self = super().create(uid, path, session, extraction_key)
        return self


class SynergiaNews(SynergiaGenericClass):
    def __init__(self, uid, resource, session):
        super().__init__(uid, resource, session)
        self.content = self._json_resource['Content']
        self.created = datetime.strptime(self._json_resource['CreationDate'], '%Y-%m-%d %H:%M:%S')
        self.unique_id = self._json_resource['Id']
        self.topic = self._json_resource['Subject']
        self.was_read = self._json_resource['WasRead']
        self.starts = datetime.strptime(self._json_resource['StartDate'], '%Y-%m-%d')
        self.ends = datetime.strptime(self._json_resource['EndDate'], '%Y-%m-%d')

    @classmethod
    def create(cls, uid=None, path=('SchoolNotices',), session=None, extraction_key='SchoolNotices'):
        self = super().create(uid, path, session, extraction_key)
        return self

    def __repr__(self):
        return f'<SynergiaNews {self.topic}>'
