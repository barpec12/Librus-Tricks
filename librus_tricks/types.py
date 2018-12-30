import datetime

import requests


class SynergiaSession:
    def __init__(self, user, api_url='https://api.librus.pl/2.0/'):
        """

        :type user: SynergiaSessionUser
        """
        self.user = user
        self.auth_headers = {'Authorization': f'Bearer {user.token}'}
        self.session = requests.session()
        self.__api_url = api_url

    def __repr__(self):
        return f'<Synergia session for {self.user}>'

    def get(self, *path, params={}):
        path_str = f'{self.__api_url}'
        for p in path:
            path_str += f'{p}/'
        response = self.session.get(
            path_str,
            headers=self.auth_headers,
            params=params
        )
        if response.status_code != 200:
            raise requests.HTTPError(f'Potencjalny błąd API Librusa'
                                     f'{response.status_code}'
                                     f'{response.url}'
                                     f'{response.text}')
        else:
            return response

    def walk(self, path=''):
        """
        Development function, zostanie w najbliższym czasie usunięta
        """
        print(requests.get(
            f'{self.__api_url}{path}',
            headers=self.auth_headers
        ).json())

    def get_timetable(self, week_start_str=None, raw=False, as_dict=False, print_on_collect=False, collect_extra=True):
        """
        Zwraca plan lekcji w postaci tablic z obiektami

        :param week_start_str: Data w formacie rrrr-mm-dd
        :type week_start_str: str
        :param raw: Określa czy chcesz dostać czystego json'a w formie tekstowej
        :type raw: bool
        :return: json in str, dict lub dict z obiektami
        """
        if raw:
            if week_start_str:
                return self.get('Timetables', params={'weekStart': week_start_str}).text
            else:
                return self.get('Timetables').text
        if as_dict:
            if week_start_str:
                return self.get('Timetables', params={'weekStart': week_start_str}).json()
            else:
                return self.get('Timetables').json()
        elif week_start_str:
            tt = self.get('Timetables', params={'weekStart': week_start_str}).json()['Timetable']
        else:
            tt = self.get('Timetables').json()['Timetable']

        fancy_tt = {}
        for date in tt.keys():
            fancy_tt[date] = []
            if print_on_collect:
                print(date)
            for l_dict in tt[date]:
                if l_dict.__len__() != 0:
                    ste = SynergiaTimetableEntry(l_dict[0], self, collect_extra=collect_extra)
                    fancy_tt[date].append(ste)
                    if print_on_collect:
                        print(ste)
        return fancy_tt

    def get_grades(self, raw=False, as_dict=False, print_on_collect=False): # TODO: tu ogólnie trzeba cokolwiek zrobić
        if raw:
            return self.get('Grades').text
        if as_dict:
            return self.get('Grades').json()

    def get_lucky_num(self):
        return self.get(
            'LuckyNumbers'
        ).json()['LuckyNumber']


class SynergiaSessionUser:
    def __init__(self, data_dict):
        self.uid = data_dict['id']
        self.token = data_dict['accessToken']
        self.name, self.surname = data_dict['studentName'].split(' ')

    def __repr__(self):
        return f'<Synergia user called {self.name} {self.surname}>'


class SynergiaLesson:
    def __init__(self, lesson_id, session, get_extra_info=False):
        """
        Obiekt, który reprezentuje daną lekcję

        :param lesson_id: ID lekcji
        :type lesson_id: str
        :param session: obiekt sesji synergii
        :type session: SynergiaSession
        :param get_extra_info: Definiuje czy przy utworzeniu obiektu, automatycznie wygenerować dodatkowe obiekty
        :type get_extra_info: bool
        """
        self.lid = lesson_id
        self.__session = session
        if get_extra_info:
            self.get_extra_info()
            self.have_extra = True
        else:
            self.have_extra = False

    def get_extra_info(self):
        r = self.__session.get(
            'Lessons', self.lid,
        ).json()['Lesson']
        self.teacher = SynergiaTeacher(r['Teacher']['Id'], self.__session)
        self.subject = SynergiaSubject(r['Subject']['Id'], self.__session)
        self.have_extra = True

    def __repr__(self):
        if self.have_extra:
            return f'<Synergia lesson {self.subject}>'
        else:
            return f'<Synergia lesson {self.lid}>'


class SynergiaClassroom:
    def __init__(self, classroom_id, session, get_extra_info=False):
        """
        Obiekt, który reprezentuje pracownie/klasę

        :param classroom_id: ID klasy
        :type classroom_id: str
        :param session: obiekt sesji synergii
        :type session: SynergiaSession
        :param get_extra_info: Definiuje czy przy utworzeniu obiektu, automatycznie wygenerować dodatkowe obiekty
        :type get_extra_info: bool
        """
        self.cid = classroom_id
        self.__session = session
        if get_extra_info:
            self.get_extra_info()
            self.have_extra = True
        else:
            self.have_extra = False

    def get_extra_info(self):
        r = self.__session.get(
            'Classrooms', self.cid
        ).json()['Classroom']
        self.name = r['Name']
        self.symbol = r['Symbol']
        self.is_common_room = r['SchoolCommonRoom']
        self.size = r['Size']
        self.have_extra = True

    def __repr__(self):
        if self.have_extra:
            return f'<Synergia classroom {self.name}>'
        else:
            return f'<Synergia classroom {self.cid}>'


class SynergiaSubject:
    def __init__(self, subject_id, session, get_extra_info=False):
        """
        Obiekt, który reprezentuje dany przedmiot

        :param subject_id: ID przedmiotu
        :type subject_id: str
        :param session: obiekt sesji synergii
        :type session: SynergiaSession
        :param get_extra_info: Definiuje czy przy utworzeniu obiektu, automatycznie wygenerować dodatkowe obiekty
        :type get_extra_info: bool
        """
        self.sid = subject_id
        self.__session = session
        if get_extra_info:
            self.get_extra_info()
            self.have_extra = True
        else:
            self.have_extra = False

    def get_extra_info(self):
        r = self.__session.get(
            'Subjects', self.sid
        ).json()['Subject']
        self.name = r['Name']
        self.sname = r['Short']
        self.is_extra = r['IsExtracurricular']
        self.have_extra = True


    def __repr__(self):
        if self.have_extra:
            return f'<Synergia subject {self.name}>'
        else:
            return f'<Synergia subject {self.sid}>'


class SynergiaTeacher:
    def __init__(self, user_id, session, get_extra_info=False):
        """
        Obiekt, który reprezentuje nauczyciela

        :param user_id: ID użytkownika (tutaj nauczyciela)
        :type user_id: str
        :param session: obiekt sesji synergii
        :type session: SynergiaSession
        :param get_extra_info: Definiuje czy przy utworzeniu obiektu, automatycznie wygenerować dodatkowe obiekty
        :type get_extra_info: bool
        """
        self.uid = user_id
        self.__session = session
        if get_extra_info:
            self.get_extra_info()
            self.have_extra = True
        else:
            self.have_extra = False

    def get_extra_info(self):
        r = self.__session.get(
            'Users', self.uid
        ).json()['User']
        self.aid = r['AccountId']
        self.name = r['FirstName']
        self.lastname = r['LastName']

    def __repr__(self):
        return f'<Synergia teacher called {self.name} {self.lastname}>'


class SynergiaVirtualClass:
    def __init__(self, vc_id, session, get_extra_info=True):
        """

        :param vc_id:
        :param session:
        :type session: SynergiaSession
        :param get_extra_info: Definiuje czy przy utworzeniu obiektu, automatycznie wygenerować dodatkowe obiekty
        :type get_extra_info: bool
        """
        self.cid = vc_id
        self.__session = session
        if get_extra_info:
            self.get_extra_info()
            self.have_extra = True
        else:
            self.have_extra = False

    def get_extra_info(self):
        r = self.__session.get(
            'VirtualClasses', self.cid
        ).json()
        r = r['VirtualClass']
        self.teacher = SynergiaTeacher(r['Teacher']['Id'], self.__session)
        self.subject = SynergiaSubject(r['Subject']['Id'], self.__session)
        self.name = r['Name']
        self.sname = r['Symbol']

    def __repr__(self):
        return f'<Synergia virtual class {self.name}>'


class SynergiaLessonEntry:
    def __init__(self, te_id, session, get_extra_info=False):
        """

        :param te_id:
        :type te_id: str
        :param session:
        :type session: SynergiaSession
        :param get_extra_info: Definiuje czy przy utworzeniu obiektu, automatycznie wygenerować dodatkowe obiekty
        :type get_extra_info: bool
        """
        self.lid = te_id
        self.__session = session
        if get_extra_info:
            self.get_extra_info()
            self.have_extra = True
        else:
            self.have_extra = False

    def get_extra_info(self):
        r = self.__session.get(
            'TimetableEntries', self.lid
        ).json()['TimetableEntry']
        self.lesson = SynergiaLesson(r['Lesson']['Id'], self.__session)
        try:
            self.virtual_class = SynergiaVirtualClass(r['VirtualClass']['Id'], self.__session)
        except:
            self.virtual_class = None
        self.date_from = datetime.datetime.strptime(r['DateFrom'], '%Y-%m-%d')
        self.date_to = datetime.datetime.strptime(r['DateTo'], '%Y-%m-%d')
        self.lesson_no = r['LessonNo']
        self.classroom = SynergiaClassroom(r['Classroom']['Id'], self.__session)

    def __repr__(self):
        return f'<Synergia lesson entry for {self.lesson}>'


class SynergiaTimetableEntry:
    def __init__(self, entry_dict, session, collect_extra=False):
        self.__session = session
        self.lesson = SynergiaLesson(entry_dict['Lesson']['Id'], self.__session, get_extra_info=collect_extra)
        try:
            self.classroom = SynergiaClassroom(entry_dict['Classroom']['Id'], self.__session, get_extra_info=collect_extra)
        except:
            self.classroom = SynergiaClassroom(entry_dict['OrgClassroom']['Id'], self.__session, get_extra_info=collect_extra)
        self.lesson_entry = SynergiaLessonEntry(entry_dict['TimetableEntry']['Id'], self.__session, get_extra_info=collect_extra)
        self.day_no = entry_dict['DayNo']
        self.subject = SynergiaSubject(entry_dict['Subject']['Id'], self.__session, get_extra_info=collect_extra)
        self.teacher = SynergiaTeacher(entry_dict['Teacher']['Id'], self.__session, get_extra_info=collect_extra)
        self.is_substitution_lesson = entry_dict['IsSubstitutionClass']
        self.is_canceled = entry_dict['IsCanceled']
        self.substitution_desc = entry_dict['SubstitutionNote']
        self.hour_from = entry_dict['HourFrom']  # TODO: zmienić na obiekt typu datetime
        self.hour_to = entry_dict['HourTo']
        try:
            self.virtual_class = SynergiaVirtualClass(entry_dict['VirtualClass']['Id'], self.__session, get_extra_info=collect_extra)
        except:
            self.virtual_class = None

    def __repr__(self):
        return f'<Synergia timetable entry {self.hour_from}-{self.hour_to} {self.lesson}>'
