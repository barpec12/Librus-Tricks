class LibrusLoginError(Exception):
    pass


class LibrusNotHandlerableError(Exception):
    pass


class SynergiaNotFound(Exception):
    pass


class LibrusInvalidPasswordError(Exception):
    pass


class SynergiaAccessDenied(Exception):
    pass


class WrongHTTPMethod(Exception):
    pass


class SynergiaInvalidRequest(Exception):
    pass


class TokenExpired(Exception):
    pass
