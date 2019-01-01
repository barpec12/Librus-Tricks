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
        self.__session = session
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
        response = self.__session.get(
            'Lessons', self.oid,
        )
        payload = response.json()['Lesson']
        self.teacher = SynergiaTeacher(payload['Teacher']['Id'], self.__session)
        self.subject = SynergiaSubject(payload['Subject']['Id'], self.__session)
        self.have_extra = True


class SynergiaTeacher(SynergiaGenericClass):
    def get_extra_info(self):
        response = self.__session.get(
            'Classrooms', self.oid
        )
        payload = response.json()['Classroom']
        self.name = payload['Name']
        self.symbol = payload['Symbol']
        self.is_common_room = payload['SchoolCommonRoom']
        self.size = payload['Size']
        self.have_extra = True


class SynergiaSubject(SynergiaGenericClass):
    def get_extra_info(self):
        response = self.__session.get(
            'Users', self.oid
        )
        payload = response.json()['User']
        self.account_id = payload['AccountId']
        self.name = payload['FirstName']
        self.lastname = payload['LastName']
        self.have_extra = True


class SynergiaVirtualClass(SynergiaGenericClass):
    def get_extra_info(self):
        response = self.__session.get(
            'VirtualClasses', self.oid
        ).json()
        payload = response['VirtualClass']
        self.teacher = SynergiaTeacher(payload['Teacher']['Id'], self.__session)
        self.subject = SynergiaSubject(payload['Subject']['Id'], self.__session)
        self.name = payload['Name']
        self.sname = payload['Symbol']
        self.have_extra = True


class SynergiaClassroom(SynergiaGenericClass):
    def get_extra_info(self):
        response = self.__session.get(
            'Classrooms', self.oid
        )
        payload = response.json()['Classroom']
        self.name = payload['Name']
        self.symbol = payload['Symbol']
        self.is_common_room = payload['SchoolCommonRoom']
        self.size = payload['Size']
        self.have_extra = True


class SynergiaLessonEntry(SynergiaGenericClass):
    def get_extra_info(self):
        response = self.__session.get(
            'TimetableEntries', self.oid
        )
        payload = response.json()['TimetableEntry']
        self.lesson = SynergiaLesson(payload['Lesson']['Id'], self.__session)
        try:
            self.virtual_class = SynergiaVirtualClass(payload['VirtualClass']['Id'], self.__session)
        except:
            self.virtual_class = None
        self.date_from = datetime.datetime.strptime(payload['DateFrom'], '%Y-%m-%d')
        self.date_to = datetime.datetime.strptime(payload['DateTo'], '%Y-%m-%d')
        self.lesson_no = payload['LessonNo']
        self.classroom = SynergiaClassroom(payload['Classroom']['Id'], self.__session)
        self.have_extra = True
