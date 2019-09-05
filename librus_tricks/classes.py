import asyncio
from datetime import datetime


class SynergiaBaseClass:
    def __init__(self, uid, resource, session):
        self.uid = uid
        self._session = session
        self._json_resource = resource

    @classmethod
    def assembly(cls, resource, session):
        self = cls(resource['Id'], resource, session)
        return self

    @classmethod
    async def create(cls, uid, path, session, extraction_key):
        """

        :param int uid:
        :param str extraction_key:
        :type session: librus_tricks.core.SynergiaClient
        :type path: list of str
        """
        response = await session.get(*path, uid)
        resource = response[extraction_key]
        self = cls(resource['Id'], resource, session=session)
        return self

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.uid} at {hex(id(self))}>'


class SynergiaTeacher(SynergiaBaseClass):
    def __init__(self, uid, resource, session=None):
        super().__init__(uid, resource, session)
        self.name = self._json_resource['FirstName']
        self.last_name = self._json_resource['LastName']

    @classmethod
    async def create(cls, uid=None, path=('Users',), session=None, extraction_key='User'):
        self = await super().create(uid, path, session, extraction_key)
        return self

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name} {self.last_name}>'

    def __str__(self):
        return f'{self.name} {self.last_name}'


class SynergiaSubject(SynergiaBaseClass):
    def __init__(self, uid, resource, session=None):
        super().__init__(uid, resource, session)
        self.name = self._json_resource['Name']
        self.short_name = self._json_resource['Short']

    @classmethod
    async def create(cls, uid=None, path=('Subjects',) , session=None, extraction_key='Subject'):
        self = await super().create(uid, path, session, extraction_key)
        return self

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name}>'

    def __str__(self):
        return self.name


class SynergiaGrade(SynergiaBaseClass):
    def __init__(self, uid, resource, session=None):
        super().__init__(uid, resource, session)
        self.add_date = datetime.strptime(self._json_resource['AddDate'], '%Y-%m-%d %H:%M:%S')
        self.date = datetime.strptime(self._json_resource['Date'], '%Y-%m-%d').date()
        self.grade = self._json_resource['Grade']
        self.is_constituent = self._json_resource['IsConstituent']
        self.semester = self._json_resource['Semester']
        self.subject = asyncio.create_task(
            SynergiaSubject.create(
                uid=self._json_resource['Subject']['Id'],
                session=session
            )
        )
        self.teacher = asyncio.create_task(
            SynergiaTeacher.create(
                uid=self._json_resource['AddedBy']['Id'],
                session=session
            )
        )
