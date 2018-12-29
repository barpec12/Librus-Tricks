import requests

from librus_tricks.types import SynergiaSessionUser
from librus_tricks.utils import get_access_token, get_auth_code, get_synergia_users, SYNERGIAAUTHURL

name = 'librus_tricks'

def ez_login(email, passwd, rtype='UserObjs'):
    """
    Ułatwia pozyskanie danych do autoryzacji do librus synergia

    :param email: Email do librus synergia
    :type email: str
    :type passwd: str
    :param rtype: Wybiera w jaki co ma zostać zwrócone na return, wybieraj między `UserObjs` lub `tokens` lub `raw`
    :type rtype: str
    """
    auth_code = get_auth_code(email, passwd)
    librus_token = get_access_token(auth_code)
    response = requests.get(
        SYNERGIAAUTHURL,
        headers={'Authorization': f'Bearer {librus_token}'}
    )
    if rtype == 'UserObjs':
        users = []
        for a in response.json()['accounts']:
            users.append(SynergiaSessionUser(a))
        return users
    elif rtype == 'tokens':
        librus_tokens = {}
        for t in response.json()['accounts']:
            librus_token[t['studentName']] = t['accessToken']
        return librus_token
    elif rtype == 'raw':
        return response.text
    else:
        raise KeyError('Zły argument dla rtype')
