import requests
from librus_tricks import exceptions, utils
from librus_tricks.types import *


class SynergiaClient:
    def __init__(self, user, api_url='https://api.librus.pl/2.0/'):
        self.user = user
        self.session = requests.session()
        self.__auth_headers = {'Authorization': f'Bearer {user.token}'}
        self.__api_url = api_url

    def __repr__(self):
        return f'<Synergia session for {self.user}>'

    def get(self, *path):
        path_str = f'{self.__api_url}'
        for p in path:
            path_str += f'{p}/'
        response = self.session.get(
            path_str, headers=self.__auth_headers
        )

        if response.status_code == 404:
            raise exceptions.SynergiaEndpointNotFound(path_str)

        return response.json()

    def get_grade(self, grade_id):
        return SynergiaGrade(grade_id, self)

    def get_grades(self, selected=None):
        if selected == None:
            return utils.get_all_grades(self)
        else:
            ids_computed = ''
            for i in selected:
                ids_computed += f'{i},'
            ids_computed += f'{selected[-1]}'
            return utils.get_objects(self, 'Grades', ids_computed, 'Grades', SynergiaGrade)
