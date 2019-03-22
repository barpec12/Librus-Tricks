import requests
from librus_tricks import exceptions, utilities
from librus_tricks.classes import *


class SynergiaClient:
    """Sesja z API Synergii"""

    def __init__(self, user, api_url='https://api.librus.pl/2.0/', user_agent='LibrusMobileApp'):
        """
        Tworzy obiekt sesji z API Synergii.

        :param librus_tricks.auth.SynergiaAuthUser user: użytkownik Synergii
        :param str api_url: url do API, NIE ZMIENIAJ GO JEŚLI NIE WIESZ DO CZEGO SŁUŻY
        """
        self.user = user
        self.session = requests.session()
        self.__auth_headers = {'Authorization': f'Bearer {user.token}', 'User-Agent': user_agent}
        self.__api_url = api_url

    def __repr__(self):
        return f'<Synergia session for {self.user}>'

    def get(self, *path, request_params=dict()):
        """
        Zwraca json'a przekonwertowany na dict'a po podaniu prawidłowego węzła

        przykład: ``session.get('Grades', '42690')``

        :param path: Ścieżka zawierająca węzeł API
        :type path: str
        :return: json przekonwertowany na dict'a
        :rtype: dict
        :raise librus_tricks.exceptions.SynergiaEndpointNotFound: nie zaleziono określonego węzła
        """
        path_str = f'{self.__api_url}'
        for p in path:
            path_str += f'{p}/'
        response = self.session.get(
            path_str, headers=self.__auth_headers, params=request_params
        )

        if response.status_code == 404:
            raise exceptions.SynergiaEndpointNotFound(path_str)
        elif response.status_code == 403:
            raise exceptions.SynergiaEndpointRequireMorePermissions(path_str)

        return response.json()

    def get_grade(self, grade_id):
        """
        Zwraca podaną ocenę

        przykład: ``session.get_grade('42690')``

        :param str grade_id: id oceny
        :return: obiekt oceny
        :rtype: librus_tricks.classes.SynergiaGrade
        """
        return SynergiaGrade(grade_id, self)

    def get_grades(self, selected=None):
        """
        Zwraca daną listę ocen

        :param selected: lista lub krotka z wybranymi ocenami, zostawienie tego parametru
        powoduje pobranie wszystkich ocen
        :type selected: list of int
        :type selected: tuple of int
        :return: krotka z ocenami
        :rtype: tuple of librus_tricks.classes.SynergiaGrade
        """
        if selected == None:
            return utilities.get_all_grades(self)
        else:
            ids_computed = ''
            for i in selected:
                ids_computed += f'{i},'
            ids_computed += f'{selected[-1]}'
            return utilities.get_objects(self, 'Grades', ids_computed, 'Grades', SynergiaGrade)

    def get_exams(self, *calendars):
        return utilities.get_exams(self, *calendars)

    def get_future_exams(self, *calendars, now=datetime.now()):
        exams_all = utilities.get_exams(self, *calendars)
        exams_future = []
        for ex in exams_all:
            if ex.date > now:
                exams_future.append(
                    ex
                )
        return exams_future

    def get_attendances(self, *att_ids):
        """

        :param att_ids:
        :return:
        :rtype: tuple of librus_tricks.classes.SynergiaAttendance
        """
        computed_ids = ''
        for atid in att_ids:
            computed_ids += atid + ','
        return utilities.get_objects(self, 'Attendances', computed_ids, 'Attendances', SynergiaAttendance)

    def get_absences(self):
        return utilities.get_filtered_attendance(self, *utilities.get_all_absence_types(self))

    def get_timetable(self, week_start=None):
        if week_start == None:
            return utilities.get_timetable(self)
        else:
            return utilities.get_timetable(self, week_start)
