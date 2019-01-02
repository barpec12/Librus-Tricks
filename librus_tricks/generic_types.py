import datetime
import librus_tricks.errors as li_err


class SynergiaGenericClass:
    def __init__(self, obj_id, session, get_extra_info=False):
        """

        :param obj_id: ID obiektu
        :type obj_id: str
        :param session: Obiekt sesji
        :type session: SynergiaSession
        :param get_extra_info: Określa czy dodatkowe dane mają zostać pobrane przy tworzeniu obiektu
        :type get_extra_info: bool
        """
        self.oid = obj_id
        self.synergia_session = session
        if get_extra_info:
            self.get_extra_info()
            self.have_extra = True
        else:
            self.have_extra = False

    def get_extra_info(self):
        raise li_err.OverrideRequired()

    def __repr__(self):
        return f'<{self.__class__.__name__} with object id {self.oid}>'


class SynergiaLesson(SynergiaGenericClass):
    def get_extra_info(self):
        response = self.synergia_session.get(
            'Lessons', self.oid,
        )
        payload = response.json()['Lesson']
        self.teacher = SynergiaTeacher(payload['Teacher']['Id'], self.synergia_session)
        self.subject = SynergiaSubject(payload['Subject']['Id'], self.synergia_session)
        self.have_extra = True


class SynergiaClassroom(SynergiaGenericClass):
    def get_extra_info(self):
        response = self.synergia_session.get(
            'Classrooms', self.oid
        )
        payload = response.json()['Classroom']
        self.name = payload['Name']
        self.symbol = payload['Symbol']
        self.is_common_room = payload['SchoolCommonRoom']
        self.size = payload['Size']
        self.have_extra = True


class SynergiaTeacher(SynergiaGenericClass):
    def get_extra_info(self):
        response = self.synergia_session.get(
            'Users', self.oid
        )
        payload = response.json()['User']
        self.account_id = payload['AccountId']
        self.name = payload['FirstName']
        self.lastname = payload['LastName']
        self.have_extra = True


class SynergiaVirtualClass(SynergiaGenericClass):
    def get_extra_info(self):
        response = self.synergia_session.get(
            'VirtualClasses', self.oid
        ).json()
        payload = response['VirtualClass']
        self.teacher = SynergiaTeacher(payload['Teacher']['Id'], self.synergia_session)
        self.subject = SynergiaSubject(payload['Subject']['Id'], self.synergia_session)
        self.name = payload['Name']
        self.sname = payload['Symbol']
        self.have_extra = True


class SynergiaSubject(SynergiaGenericClass):
    def get_extra_info(self):
        response = self.synergia_session.get(
            'Subjects', self.oid
        )
        payload = response.json()['Subject']
        self.name = payload['Name']
        self.shortname = payload['Short']
        self._no = payload['No']
        self.is_extracirricular = payload['IsExtracurricular']
        self.id_block_lesson = payload['IsBlockLesson']
        self.have_extra = True


class SynergiaLessonEntry(SynergiaGenericClass):
    def get_extra_info(self):
        response = self.synergia_session.get(
            'TimetableEntries', self.oid
        )
        payload = response.json()['TimetableEntry']
        self.lesson = SynergiaLesson(payload['Lesson']['Id'], self.synergia_session)
        if 'VirtualClass' in payload.keys():
            self.virtual_class = SynergiaVirtualClass(payload['VirtualClass']['Id'], self.synergia_session)
        else:
            self.virtual_class = None
        self.date_from = datetime.datetime.strptime(payload['DateFrom'], '%Y-%m-%d')
        self.date_to = datetime.datetime.strptime(payload['DateTo'], '%Y-%m-%d')
        self.lesson_no = payload['LessonNo']
        self.classroom = SynergiaClassroom(payload['Classroom']['Id'], self.synergia_session)
        self.have_extra = True

class SynergiaAttendance(SynergiaGenericClass):
    def __init__(self, atted_dict, session, get_extra_info=False):
        super().__init__(atted_dict['Id'], session, get_extra_info)
        self.attendance_date = datetime.datetime.strptime(atted_dict['Date'], '%Y-%m-%d')
        self.lesson_no = atted_dict['LessonNo']
        self.attendance_added = datetime.datetime.strptime(atted_dict['Date'], '%Y-%m-%d %H:%M:%S')
        self.teacher = atted_dict['AddedBy']['Id']
        self.student = atted_dict['Student']['Id']
        self.type= atted_dict['Type']['Id']

    def get_extra_info(self):
        self.teacher = SynergiaTeacher(self.teacher, self.synergia_session)
        self.type = SynergiaAttendanceType(self.type, self.synergia_session)

        self.have_extra = True

class SynergiaAttendanceType:
    def __init__(self, type_dict):
        self.oid=  type_dict['Id']
        self.name = type_dict['Name']
        self.short_name = type_dict['Short']
        self.is_standart = type_dict['Standard']
        self.color = type_dict['ColorRGB']
        self.is_presence_kind = type_dict['IsPresenceKind']
        self.order = type_dict['Order']

    @staticmethod
    def gen_from_id(oid, session):
        """

        :param oid:
        :param session:
        :type session: librus_tricks.SynergiaSession
        :return:
        """
        response = session.get(

        )

