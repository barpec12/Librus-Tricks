import requests

from librus_tricks import cache as cache_lib
from librus_tricks import exceptions, tools
from librus_tricks.classes import *
from librus_tricks.messages import MessageReader
from datetime import timedelta


class SynergiaClient:
    """Sesja z API Synergii"""

    def __init__(self, user, api_url='https://api.librus.pl/2.0', user_agent='LibrusMobileApp',
                 cache=cache_lib.AlchemyCache(), synergia_user_passwd=None):
        """

        :param user:
        :param api_url:
        :param user_agent:
        :param cache:
        :param synergia_user_passwd:
        """
        self.user = user
        self.session = requests.session()

        if cache_lib.CacheBase in cache.__class__.__bases__:
            self.cache = cache
            self.li_session = self
        else:
            raise exceptions.InvalidCacheManager(f'{cache} can not be a cache object!')

        if synergia_user_passwd:
            self.message_reader = MessageReader(self.user.login, synergia_user_passwd, cache_backend=self.cache)
        else:
            self.message_reader = None

        self.__auth_headers = {'Authorization': f'Bearer {user.token}', 'User-Agent': user_agent}
        self.__api_url = api_url

    def __repr__(self):
        return f'<Synergia session for {self.user}>'

    @staticmethod
    def assembly_path(*elements, prefix='', suffix='', sep='/'):
        for el in elements:
            prefix += sep + str(el)
        return prefix + suffix

    # HTTP part

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
        path_str = self.assembly_path(*path, prefix=self.__api_url)
        response = self.session.get(
            path_str, headers=self.__auth_headers, params=request_params
        )
        print(path_str)

        if response.status_code >= 400:
            raise {
                500: Exception('Server error'),
                404: exceptions.SynergiaNotFound(path_str),
                403: exceptions.SynergiaForbidden(response.json()),
                401: exceptions.SynergiaAccessDenied(response.json()),
                400: exceptions.SynergiaInvalidRequest(response.json()),
            }[response.status_code]

        return response.json()

    def post(self, *path, request_params=None):
        if request_params is None:
            request_params = dict()
        path_str = self.assembly_path(*path, prefix=self.__api_url)
        response = self.session.post(
            path_str, headers=self.__auth_headers, params=request_params
        )

        if response.status_code >= 400:
            raise {
                500: Exception('Server error'),
                404: exceptions.SynergiaNotFound(response.json()),
                403: exceptions.SynergiaForbidden(response.json()),
                401: exceptions.SynergiaAccessDenied(response.json()),
                400: exceptions.SynergiaInvalidRequest(response.json()),
            }[response.status_code]

        return response.json()

    # Cache

    def get_cached_response(self, *path, http_params=None, max_lifetime=timedelta(hours=1)):
        uri = self.assembly_path(*path, prefix=self.__api_url)
        response_cached = self.cache.get_query(uri)

        if response_cached is None:
            http_response = self.get(*path, request_params=http_params)
            self.cache.add_query(uri, http_response)
            return http_response

        age = datetime.now() - response_cached.last_load

        if age > max_lifetime:
            http_response = self.get(*path, request_params=http_params)
            self.cache.del_query(uri)
            self.cache.add_query(uri, http_response)
            return http_response
        return response_cached.response

    def get_cached_object(self, uid, cls, max_lifetime=timedelta(hours=1)):
        requested_object = self.cache.get_object(uid, cls)

        if requested_object is None:
            requested_object = cls.create(uid=uid, session=self)
            self.cache.add_object(uid, cls, requested_object._json_resource)
            return requested_object

        age = datetime.now() - requested_object.last_load

        if age > max_lifetime:
            requested_object = cls.create(uid=uid, session=self)
            self.cache.del_object(uid)
            self.cache.add_object(uid, cls, requested_object._json_resource)

        return requested_object

    # API query part

    def return_objects(self, *path, cls, extraction_key=None, lifetime=timedelta(minutes=1)):
        """

        :param path:
        :param cls:
        :param extraction_key:
        :param lifetime:
        :return:
        """
        raw = self.get_cached_response(*path, max_lifetime=lifetime)

        if extraction_key is None:
            extraction_key = SynergiaGenericClass.auto_extract(raw)

        raw = raw[extraction_key]

        stack = []

        for stored_payload in raw:
            stack.append(cls.assembly(stored_payload, self))

        return tuple(stack)

    def grades(self, *grades):
        """
        Zwraca daną listę ocen.

        :return: krotka z ocenami
        :rtype: tuple of librus_tricks.classes.SynergiaGrade
        """
        if grades.__len__() == 0:
            return self.return_objects('Grades', cls=SynergiaGrade, extraction_key='Grades')
        else:
            ids_computed = self.assembly_path(*grades, sep=',', suffix=grades[-1])[1:]
            return self.return_objects('Grades', ids_computed, cls=SynergiaGrade, extraction_key='Grades')

    def attendances(self, *attendances):
        """

        :param attendances:
        :return:
        :rtype: tuple of librus_tricks.classes.SynergiaAttendance
        """
        if attendances.__len__() == 0:
            return self.return_objects('Attendances', cls=SynergiaAttendance, extraction_key='Attendances')
        else:
            ids_computed = self.assembly_path(*attendances, sep=',', suffix=attendances[-1])[1:]
            return self.return_objects('Attendances', ids_computed, cls=SynergiaGrade, extraction_key='Attendances')

    def exams(self, *exams):
        """

        :param exams:
        :return:
        :rtype: tuple of librus_tricks.classes.SynergiaExam
        """
        if exams.__len__() == 0:
            return self.return_objects('HomeWorks', cls=SynergiaExam, extraction_key='HomeWorks')
        else:
            ids_computed = self.assembly_path(*exams, sep=',', suffix=exams[-1])[1:]
            return self.return_objects('HomeWorks', ids_computed, cls=SynergiaExam, extraction_key='HomeWorks')

    def colors(self, *colors):
        """

        :param exams:
        :return:
        :rtype: tuple of librus_tricks.classes.SynergiaColors
        """
        if colors.__len__() == 0:
            return self.return_objects('Colors', cls=SynergiaColor, extraction_key='Colors')
        else:
            ids_computed = self.assembly_path(*colors, sep=',', suffix=colors[-1])
            return self.return_objects('Colors', ids_computed, cls=SynergiaColor, extraction_key='Colors')

    def timetable(self, for_date=datetime.now()):
        """

        :param for_date:
        :return:
        :rtype: Dict[datetime.date, List[librus_tricks.classes.SynergiaTimetableEvent]]
        """
        monday = tools.get_actual_monday(for_date).isoformat()
        r = self.get('Timetables', request_params={'weekStart': monday})
        return SynergiaTimetable.assembly(r['Timetable'], self)

    @property
    def today_timetable(self):
        """

        :return:
        :rtype: list of librus_tricks.classes.SynergiaTimetableEvent
        """
        return self.timetable().lessons[datetime.now().date()]

    @property
    def tomorrow_timetable(self):
        """

        :return:
        :rtype: list of librus_tricks.classes.SynergiaTimetableEvent
        """
        return self.timetable(datetime.now() + timedelta(days=1)).lessons[(datetime.now() + timedelta(days=1)).date()]

    def messages(self, *messages):
        """

        :param exams:
        :return:
        :rtype: tuple of librus_tricks.classes.SynergiaColors
        """
        if messages.__len__() == 0:
            return self.return_objects('Messages', cls=SynergiaNativeMessage, extraction_key='Messages')
        else:
            ids_computed = self.assembly_path(*messages, sep=',', suffix=messages[-1])[1:]
            return self.return_objects('Messages', ids_computed, cls=SynergiaNativeMessage, extraction_key='Messages')

    def news_feed(self):
        return self.return_objects('SchoolNotices', cls=SynergiaNews, extraction_key='SchoolNotices')
