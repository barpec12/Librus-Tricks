class SynergiaBaseClass:
    def __init__(self, uid, resource, session=None):
        self.uid = uid
        self._session = session
        self._json_resource = resource

    @classmethod
    def assembly(cls, resource):
        self = cls(resource['Id'], resource)
        return self

    @classmethod
    async def create(cls, uid, extraction_key, path, session):
        """

        :param int uid:
        :param str extraction_key:
        :type session: librus_tricks.core.SynergiaClient
        :type path: list of str
        """
        response = await session.get(session.assembly_path(*path, uid))
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

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.name} {self.last_name}>'

    def __str__(self):
        return f'{self.name} {self.last_name}'