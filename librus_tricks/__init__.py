import requests

from librus_tricks.types import SynergiaSessionUser
from librus_tricks.utils import get_access_token, get_auth_code, get_synergia_users, SYNERGIAAUTHURL, try_until_die

name = 'librus_tricks'

def ez_login(email, passwd, rtype='UserObjs'):
    """
    Ułatwia pozyskanie danych do autoryzacji do librus synergia

    :param email: Email do librus synergia
    :type email: str
    :type passwd: str
    :param rtype: Wybiera w jaki co ma zostać zwrócone na return, wybieraj między `UserObjs` lub `tokens`
    :type rtype: str
    """
    auth_code = get_auth_code(email, passwd)
    librus_token = get_access_token(auth_code)
    response = try_until_die(librus_token)
    if rtype == 'UserObjs':
        users = []
        for a in response:
            users.append(SynergiaSessionUser(a))
        return users
    elif rtype == 'tokens':
        librus_tokens = {}
        for t in response:
            librus_tokens[t['studentName']] = t['accessToken']
        return librus_token
    else:
        raise KeyError('Zły argument dla rtype')
