import requests

from librus_tricks import cache
from librus_tricks import exceptions, utilities
from librus_tricks.classes import *


class SynergiaClient:
    """Sesja z API Synergii"""

    def __init__(self, user, api_url='https://api.librus.pl/2.0/', user_agent='LibrusMobileApp',
                 cache_location='cache.sqlite', custom_cache_object=None):
        """
        Tworzy obiekt sesji z API Synergii.

        :param librus_tricks.auth.SynergiaAuthUser user: użytkownik Synergii
        :param str api_url: url do API, NIE ZMIENIAJ GO JEŚLI NIE WIESZ DO CZEGO SŁUŻY
        :param str user_agent: określa jak ma się przedstawiać nasza sesja
        :param str cache_location: określa lokalizację bazy danych z cache, ustaw ``:memory:``
        aby utworzyć bazę danych w pamięci operacyjnej
        """
        self.user = user
        self.session = requests.session()
        if custom_cache_object is not None:
            self.cache = custom_cache_object
        else:
            self.cache = cache.SQLiteCache(db_location=cache_location)
        self.__auth_headers = {'Authorization': f'Bearer {user.token}', 'User-Agent': user_agent}
        self.__api_url = api_url

    def __repr__(self):
        return f'<Synergia session for {self.user}>'

    def get(self, *path, request_params=None):
        """
        Zwraca json'a przekonwertowany na dict'a po podaniu prawidłowego węzła

        przykład: ``session.get('Grades', '42690')``

        :param path: Ścieżka zawierająca węzeł API
        :type path: str
        :return: json przekonwertowany na dict'a
        :rtype: dict
        :raise librus_tricks.exceptions.SynergiaEndpointNotFound: nie zaleziono określonego węzła
        """
        if request_params is None:
            request_params = dict()
        path_str = f'{self.__api_url}'
        for p in path:
            path_str += f'{p}/'
        response = self.session.get(
            path_str, headers=self.__auth_headers, params=request_params
        )

        if response.status_code == 404:
            raise exceptions.SynergiaNotFound(path_str)
        elif response.status_code == 403:
            raise exceptions.SynergiaAccessDenied(path_str)
        elif response.status_code == 400:
            raise exceptions.SynergiaInvalidRequest(response.json()['Message'])

        return response.json()

    def do_request(self, *path, method='POST', request_params=None):
        if request_params is None:
            request_params = dict()
        path_str = f'{self.__api_url}'
        for p in path:
            path_str += f'{p}/'
        if method == 'POST':
            response = self.session.post(
                path_str, headers=self.__auth_headers, params=request_params
            )
        else:
            raise exceptions.WrongHTTPMethod('Nie obsługiwane zapytanie HTTP')

        if response.status_code == 404:
            raise exceptions.SynergiaNotFound(path_str)
        elif response.status_code == 403:
            raise exceptions.SynergiaAccessDenied(path_str)

        return response.json()

    def get_grade(self, grade_id):
        """
        Zwraca podaną ocenę.

        przykład: ``session.get_grade('42690')``

        :param str grade_id: id oceny
        :return: obiekt oceny
        :rtype: librus_tricks.classes.SynergiaGrade
        """
        return SynergiaGrade(grade_id, self)

    def get_grades(self, selected=None):
        """
        Zwraca daną listę ocen.

        :param selected: lista lub krotka z wybranymi ocenami, zostawienie tego parametru
        powoduje pobranie wszystkich ocen
        :type selected: list of int
        :type selected: tuple of int
        :return: krotka z ocenami
        :rtype: tuple of librus_tricks.classes.SynergiaGrade
        """
        if selected is None:
            return utilities.get_all_grades(self)
        else:
            ids_computed = ''
            for i in selected:
                ids_computed += f'{i},'
            ids_computed += f'{selected[-1]}'
            return utilities.get_objects(self, 'Grades', ids_computed, 'Grades', SynergiaGrade)

    def get_exams(self, *calendars, only_future=True, now=datetime.now()):
        """
        Zwraca listę wszystkich egzaminów w obecnym miesiącu. Pozostawienie ``calendars`` pustym pobiera
        sprawdziany z wszystkich kalendarzy.

        :param str calendars: str zawierające id kalendarza
        :param bool only_future: bool określający czy ma pobierać tylko przyszłe sprawdziany
        :param datetime.datetime now: obiekt datetime, który określa od którego momentu ma pobierać przyszłe sprawdziany
        :return: lista zawierająca sprawdziany
        :rtype: list of librus_tricks.classes.SynergiaExam
        """
        if only_future:
            return [ex for ex in utilities.get_exams(self, *calendars) if ex.date > now.date()]
        else:
            return utilities.get_exams(self, *calendars)

    def get_attendances(self, *att_ids):
        """
        Zwraca krotkę z wszystkimi (nie)obecnościami lub zwolnieniami. Jeśli parametr ``att_ids`` zawiera id,
        pobiera tylko podaną frekwencję.

        :param att_ids: id danych obiektów frekwencji
        :return: krotka z frekwencją
        :rtype: tuple of librus_tricks.classes.SynergiaAttendance
        """
        computed_ids = ''
        for atid in att_ids:
            computed_ids += atid + ','
        return utilities.get_objects(self, 'Attendances', computed_ids, 'Attendances', SynergiaAttendance)

    def get_absences(self):
        return utilities.get_filtered_attendance(self, *utilities.get_all_absence_types(self))

    def get_timetable(self, week_start=None):
        if week_start is None:
            return utilities.get_timetable(self)
        else:
            return utilities.get_timetable(self, week_start)

    def get_news(self, unseen_only=False):
        ns = utilities.get_school_feed(self)
        if unseen_only:
            return [x for x in ns if not x.was_read]
        else:
            return ns

    def get_lucky_number(self):
        """
        Zwraca szczęśliwy numerek.

        :return: szczęśliwy numerek
        :rtype: int
        """
        return int(self.get('LuckyNumbers')['LuckyNumber']['LuckyNumber'])

    def get_teacher_free_days(self, only_future=True, now=datetime.now()):
        return utilities.get_teachers_free_days(self, only_future, now)

    def get_school_free_days(self, only_future=True, now=datetime.now()):
        return utilities.get_free_days(self, only_future, now)

    def get_all_teachers(self, *teachers_ids):
        computed_ids = ''
        for atid in teachers_ids:
            computed_ids += atid + ','
        return utilities.get_objects(self, 'Users', computed_ids, 'Users', SynergiaTeacher)

    def is_school_free_date(self, now=datetime.now()):
        """
        Zwraca czy dzisiejszy dzień jest dniem wolnym, jeśli jest zwracany jest obiekt dnia wolnego, jeśli jest to
        normalny dzień, zwracany jest False.

        :param datetime.datetime now: obiekt datetime, który określa od teraźniejszość
        :rtype: librus_tricks.classes.SynergiaSchoolFreeDays
        """
        free_days = self.get_school_free_days(only_future=False)
        for free_day in free_days:
            if free_day.starts <= now.date() <= free_day.ends:
                return free_day
        return False

    def csync(self, oid, cls):
        return self.cache.sync(oid, cls, self)

    def preload_cache(self):
        objs = (
            *utilities.get_all_attendance_types(self),
            *self.get_all_teachers(),
            *utilities.get_objects(self, 'Subjects', '', 'Subjects', SynergiaSubject)
        )
        for at in objs:
            self.csync(at.oid, at.__class__)

    # TODO: Dodać pobranie wybranego przedmiotu `get_subject`
    # TODO: Dodać pobieranie wszystkich przedmiotów `get_subjects`
