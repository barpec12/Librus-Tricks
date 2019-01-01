import requests

from . import errors as li_err
from .advanced_types import SynergiaGrade, SynergiaTimetableEntry


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

        if response.status_code == 401:
            raise li_err.TokenExpired('Token nagle wygasł, odczekaj 20 minut')
        return response

    def walk(self, path=''):
        """
        Development function, zostanie w najbliższym czasie usunięta
        """
        print(requests.get(
            f'{self.__api_url}{path}',
            headers=self.auth_headers
        ).json())

    def get_timetable(self, week_start_str=None, type='obj', print_on_collect=False, collect_extra=True):
        """
        Zwraca plan lekcji w postaci tablic z obiektami

        :param week_start_str: Data w formacie rrrr-mm-dd
        :type week_start_str: str
        :param type: Określa typ obiektu, który otrzymujesz na wyjściu (raw, as_dict, obj)
        :type type: str
        :param raw: Określa czy chcesz dostać czystego json'a w formie tekstowej
        :type raw: bool
        :return: json in str, dict lub dict z obiektami
        """
        if type == 'raw':
            if week_start_str:
                return self.get('Timetables', params={'weekStart': week_start_str}).text
            else:
                return self.get('Timetables').text
        elif type == 'as_dict':
            if week_start_str:
                return self.get('Timetables', params={'weekStart': week_start_str}).json()
            else:
                return self.get('Timetables').json()
        elif type == 'obj':
            if week_start_str:
                tt = self.get('Timetables', params={'weekStart': week_start_str}).json()['Timetable']
            else:
                tt = self.get('Timetables').json()['Timetable']
        else:
            raise li_err.WrongOption('Podana opcja jest nie poprawna, wybierz pomiędzy "obj", "as_dict" i "raw"')

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

    def get_grades(self, type='obj', print_on_collect=False, collect_extra=False):
        if type == 'raw':
            return self.get('Grades').text
        elif type == 'as_dict':
            return self.get('Grades').json()
        elif type == 'obj':
            grades_list = self.get('Grades')
            grades_list = grades_list.json()['Grades']
        else:
            raise li_err.WrongOption('Podana opcja jest nie poprawna, wybierz pomiędzy "obj", "as_dict" i "raw"')

        obj_grades = {}
        for grade_source in grades_list:
            sg = SynergiaGrade(grade_source, self, get_extra_info=collect_extra)
            if not (sg.subject.oid in obj_grades.keys()):
                obj_grades[sg.subject.oid] = list()
            obj_grades[sg.subject.oid].append(sg)
            if print_on_collect:
                print(grade_source)
                print(sg)
        return obj_grades

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
