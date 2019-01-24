import json
from time import sleep

import requests

from .core_types import SynergiaSessionUser
from .generic_types import SynergiaSubject

# config line
REDIRURI = 'http://localhost/bar'
LOGINURL = 'https://portal.librus.pl/rodzina/login/action'
OAUTHURL = 'https://portal.librus.pl/oauth2/access_token'
SYNERGIAAUTHURL = 'https://portal.librus.pl/api/SynergiaAccounts'
CLIENTID = 'wmSyUMo8llDAs4y9tJVYY92oyZ6h4lAt7KCuy0Gv'
LIBRUSLOGINURL = f'https://portal.librus.pl/oauth2/authorize?client_id={CLIENTID}&redirect_uri={REDIRURI}&response_type=code'

web_crawler = requests.session()
# Auth utilities

def get_auth_code(email, passwd):
    """
    Zamienia login i hasło na kod oauth (chyba)

    :param email: email do portal librus
    :type email: str
    :param passwd: hasło do portal librus
    :type passwd: str
    :return: kod autoryzacyjny
    """
    site = web_crawler.get(LIBRUSLOGINURL)
    csrf_token = site.text[
                 site.text.find('name="csrf-token" content="') + 27:site.text.find('name="csrf-token" content="') + 67]

    login_response_redir = web_crawler.post(
        LOGINURL,
        data=json.dumps({'email': email, 'password': passwd}),
        headers={'X-CSRF-TOKEN': csrf_token, 'Content-Type': 'application/json'}
    )

    if login_response_redir.status_code != 200:
        raise requests.exceptions.HTTPError('Zły login lub hasło lub inny błąd związany z autoryzacją')

    redir_addr = login_response_redir.json()['redirect']
    access_code = web_crawler.get(redir_addr, allow_redirects=False).headers['location'][26:]
    return access_code


def get_access_token(auth_code):
    """
    Zamienia kod autoryzacyjny na token

    :param auth_code: kod autoryzacyjny
    :type auth_code: str
    :return: token
    """
    return requests.post(
        OAUTHURL,
        data={
            'grant_type': 'authorization_code',
            'code': auth_code,
            'client_id': CLIENTID,
            'redirect_uri': REDIRURI
        }
    ).json()['access_token']




def try_many_times(access_token, print_requests=False, connecting_tries=10):
    """
    Funkcja pomocnicza do get_synergia_users

    :return: accounts
    """
    try:
        for connection_try in range(0, connecting_tries):
            try:
                response = requests.get(
                    SYNERGIAAUTHURL,
                    headers={'Authorization': f'Bearer {access_token}'}
                ).json()
                if print_requests:
                    print(response)
                accounts = response['accounts']
                return accounts
            except:
                if print_requests:
                    print(f'Próba uwierzytelnienia numer {connection_try}')
            sleep(1.5)
    except:
        raise ConnectionError('Serwer librusa ma problem z prostymi zapytaniami...')

def get_synergia_users(access_token, print_credentials=False):
    """

    :param access_token:
    :param print_credentials:
    :return:
    """
    accounts = try_many_times(access_token)
    users = []
    for d in accounts:
        if print_credentials:
            print(json.dumps(d))
        users.append(SynergiaSessionUser(d))
    return users

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
    response = try_many_times(librus_token)
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

# Convert tools

def convert_grade_keys(grades_dict, session):
    """

    :param grades_dict:
    :type grades_dict: dict
    :type session: librus_tricks.SynergiaSession
    :return:
    """
    new_dict = dict()
    for s in grades_dict.keys():
        new_key = SynergiaSubject(s, session, get_extra_info=True)
        new_dict[new_key] = grades_dict[s][:]

    return new_dict

