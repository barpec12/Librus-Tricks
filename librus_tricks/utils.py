import json

import requests

from .types import SynergiaSessionUser

# config line
REDIRURI = 'http://localhost/bar'
LOGINURL = 'https://portal.librus.pl/rodzina/login/action'
OAUTHURL = 'https://portal.librus.pl/oauth2/access_token'
SYNERGIAAUTHURL = 'https://portal.librus.pl/api/SynergiaAccounts'
CLIENTID = 'wmSyUMo8llDAs4y9tJVYY92oyZ6h4lAt7KCuy0Gv'
LIBRUSLOGINURL = f'https://portal.librus.pl/oauth2/authorize?client_id={CLIENTID}&redirect_uri={REDIRURI}&response_type=code'


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
    web_crawler = requests.session()
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
    for connection_try in range(0, connecting_tries):
        try:
            response = requests.get(
                SYNERGIAAUTHURL,
                headers={'Authorization': f'Bearer {access_token}'}
            ).json()
            accounts = response['accounts']
            return accounts
        except:
            raise ConnectionError('Serwer synergi nie odpowiada')

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
