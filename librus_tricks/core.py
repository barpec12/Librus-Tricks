import httpx
from datetime import timedelta, datetime
from .cache import cache_manager as cm, SkeletonCache
from .classes import *


class SynergiaClient:
    def __init__(self, user, api_url='https://api.librus.pl/2.0/', user_agent='LibrusMobileApp', cache_manager=cm):
        self.user = user
        self.httpx = httpx.AsyncClient()
        if isinstance(cache_manager.__class__, SkeletonCache):
            raise Exception('Wrong cache implementation')
        self.cache = cache_manager

        self.__auth_headers = {'Authorization': f'Bearer {user.token}', 'User-Agent': user_agent}
        self.__api_url = api_url

    @staticmethod
    def assembly_path(*elements, prefix='', suffix='', sep='/'):
        for el in elements:
            prefix += sep + str(el)
        return prefix + suffix

    async def get(self, *path, http_params=None):
        if http_params is None:
            http_params = dict()

        uri = self.assembly_path(*path, prefix=self.__api_url)

        response = await self.httpx.get(uri, headers=self.__auth_headers, params=http_params)

        # TODO: add errors

        return response.json()

    async def get_cached(self, *path, http_params=None, max_lifetime=timedelta(hours=1)):
        uri = self.assembly_path(*path, prefix=self.__api_url)
        response_cached = self.cache.get_query(uri)
        if response_cached is None:
            http_response = await self.get(*path, http_params=http_params)
            self.cache.add_query(uri, http_response)
            return http_response
        age = datetime.now() - response_cached.last_load
        if age > max_lifetime:
            http_response = await self.get(*path, http_params=http_params)
            self.cache.del_query(uri)
            self.cache.add_query(uri, http_response)
            return http_response
        return response_cached.response

    async def post(self, *path, payload, http_params=None):
        if http_params is None:
            http_params = dict()

        uri = self.assembly_path(*path, prefix=self.__api_url)

        response = await self.httpx.post(uri, data=payload, headers=self.__auth_headers, params=http_params)

        # TODO: add errors

        return response.json()

    async def return_objects(self, *path, cls, extraction_key, lifetime=timedelta(hours=3)):
        raw = (await self.get_cached(*path, max_lifetime=lifetime))[extraction_key]
        output = []
        for obj in raw:
            output.append(cls.assembly(obj, self))

        return output

    async def return_subjects(self):
        return await self.return_objects('Subjects', cls=SynergiaSubject, extraction_key='Subjects')

    async def return_teachers(self):
        return await self.return_objects('Users', cls=SynergiaTeacher, extraction_key='Users')

    async def return_grades(self):
        return await self.return_objects('Grades', cls=SynergiaGrade, extraction_key='Grades')
