import json
from time import sleep

import requests
import logging

from . import exceptions

# Some globals
REDIRURI = 'http://localhost/bar'
LOGINURL = 'https://portal.librus.pl/rodzina/login/action'
OAUTHURL = 'https://portal.librus.pl/oauth2/access_token'
SYNERGIAAUTHURL = 'https://portal.librus.pl/api/SynergiaAccounts'
FRESHURL = 'https://portal.librus.pl/api/SynergiaAccounts/fresh/{login}'
CLIENTID = 'wmSyUMo8llDAs4y9tJVYY92oyZ6h4lAt7KCuy0Gv'
LIBRUSLOGINURL = f'https://portal.librus.pl/oauth2/authorize?client_id={CLIENTID}&redirect_uri={REDIRURI}&response_type=code'

# Creating session
auth_session = requests.session()


# Defining auth classes

class SynergiaAuthUser:
    def __init__(self, data_dict):
        """
        Tworzy obiekt użytkownika Synergii zawierający dane do uwierzytelniania.

        :param dict data_dict: dict zawierający podstawowe dane do logowania
        """
        self.uid = data_dict['id']
        self.login = data_dict['login']
        self.token = data_dict['accessToken']
        self.name, self.surname = data_dict['studentName'].split(' ')

    @property
    def is_authenticated(self):
        """Sprawdza czy dany użytkownik zawiera nieprzeterminowane tokeny"""
        test = requests.get('https://api.librus.pl/2.0/Me', headers={'Authorization': f'Bearer {self.token}'})
        if test.status_code == 401:
            return False
        else:
            return True

    def __repr__(self):
        return f'<SynergiaAuthSession for {self.name} {self.surname} based on ' \
            f'token {self.token[:6] + "..." + self.token[-6:]}>'

    def __str__(self):
        return f'{self.name} {self.surname}'


def oauth_librus_code(email, passwd, revalidation=False):
    """
    Wrapper podszywa się pod aplikację i próbuje otrzymać kod OAuth

    :param str email: email do aplikacji Librusa
    :param str passwd: hasło do aplikacji Librusa
    :param bool revalidation: zmienna odpowiadająca za
    :return: kod OAUTH
    :rtype: str
    :raises librus_tricks.exceptions.LibrusLoginError: zły login lub hasło lub inny błąd związany z autoryzacją
    """
    if revalidation:
        mini_session = auth_session.get(LIBRUSLOGINURL, allow_redirects=False)
        access_code = mini_session.headers['location'][26:]
        return access_code
    site = auth_session.get(LIBRUSLOGINURL)
    csrf_token = site.text[
                 site.text.find('name="csrf-token" content="') + 27:site.text.find('name="csrf-token" content="') + 67
                 ]
    login_response_redir = auth_session.post(
        LOGINURL,
        data=json.dumps({'email': email, 'password': passwd}),
        headers={'X-CSRF-TOKEN': csrf_token, 'Content-Type': 'application/json'}
    )

    if login_response_redir.status_code == 401:
        raise exceptions.LibrusLoginError(
            f'Zły login lub hasło lub inny błąd związany z autoryzacją ({login_response_redir.json()})')
    elif login_response_redir.status_code == 403:
        raise exceptions.LibrusInvalidPasswordError(
            f'403 - złe hasło lub email ({login_response_redir.json()["errors"]})')

    redir_addr = login_response_redir.json()['redirect']
    access_code = auth_session.get(redir_addr, allow_redirects=False).headers['location'][26:]
    return access_code


def get_synergia_token(auth_code):
    """

    :param str auth_code: kod OAUTH z aplikacji Librusa
    :return: Kod ogólny do API Synergii
    :rtype: str
    """
    return auth_session.post(
        OAUTHURL,
        data={
            'grant_type': 'authorization_code',
            'code': auth_code,
            'client_id': CLIENTID,
            'redirect_uri': REDIRURI
        }
    ).json()['access_token']


def try_to_fetch_logins(access_token, connecting_tries=10):
    """

    :param str access_token: token ogólny do API Synergii
    :param bool print_requests: zmienna warunkująca wyświetlanie kolejnych zapytań
    :param int connecting_tries: zmienna określająca ilość ewentualnych powtórzeń
    :return: dict zawierający konta
    :rtype: dict
    """
    logging.debug('connecting_tries is set to 10 tries')
    try:
        for connection_try in range(0, connecting_tries):
            try:
                response = auth_session.get(
                    SYNERGIAAUTHURL,
                    headers={'Authorization': f'Bearer {access_token}'}
                ).json()
                logging.debug(response)
                accounts = response['accounts']
                return accounts
            except:
                logging.debug(f'try numer {connection_try}')
            sleep(1.5)
    except:
        raise exceptions.LibrusNotHandlerableError('Serwer librusa ma problem z prostymi zapytaniami...')


def get_avaiable_users(access_token):
    """
    Tworzy listę dostępnych użytkowników.

    :param str access_token: token ogólny do API Synergii
    :param bool print_credentials: wyświetlaj kolejne dostępne tożsamości
    :return: lista dostępnych użytkowników
    :rtype: list of librus_tricks.auth.SynergiaAuthUser
    """
    accounts = try_to_fetch_logins(access_token)
    users = []
    for d in accounts:
        logging.debug(json.dumps(d))
        users.append(SynergiaAuthUser(d))
    return users


def get_new_token(login, email, passwd):
    """
    Wymusza utworzenie nowego tokenu ogólnego do API Synergii.

    :param str login: login do Synergii
    :param str email: email do aplikacji Librusa
    :param str passwd: hasło do aplikacji Librusa
    :return: nowy token ogólny do API Synergii
    """
    auth_session.get(
        FRESHURL.format(login=login)
    )
    return get_synergia_token(oauth_librus_code(email, passwd, revalidation=True))


def aio(email, passwd, fetch_index=0, force_revalidation_method=False):
    """
    aio (All-In-One) ułatwia otrzymanie danych do logowania i utworzenia sesji.

    :param str email: email do aplikacji Librusa
    :param str passwd: hasło do aplikacji Librusa
    :param int fetch_index: wybór konta do Synergii
    :return: użytkownik Synergii
    :rtype: librus_tricks.auth.SynergiaAuthUser
    """
    oauth_code = oauth_librus_code(email, passwd, revalidation=force_revalidation_method)
    logging.debug(f'oauth code starts with {oauth_code[:11]}')
    synergia_token = get_synergia_token(oauth_code)
    logging.debug(f'synergia master token starts with {synergia_token[:11]}')
    api_users = get_avaiable_users(synergia_token)
    logging.debug(f'users fetched {[au.__str__() for au in api_users]}')
    u = api_users[fetch_index]
    logging.debug(f'selected user with index {fetch_index} -> {[au.__str__() for au in api_users][0]}')
    logging.debug(f'checking user\'s credentials')
    if not u.is_authenticated:
        logging.debug('renewing user\'s token...')
        synergia_token = get_new_token(u.login, email, passwd)
        api_users = get_avaiable_users(synergia_token)
        u = api_users[fetch_index]
    return u
