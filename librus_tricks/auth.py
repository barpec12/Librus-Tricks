from time import sleep

import json
import requests

from . import exeptions

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

class SynergiaAuthSession:
    def __init__(self, data_dict):
        self.uid = data_dict['id']
        self.login = data_dict['login']
        self.token = data_dict['accessToken']
        self.name, self.surname = data_dict['studentName'].split(' ')

    @property
    def is_authenticated(self):
        test = requests.get('https://api.librus.pl/2.0/Me', headers={'Authorization': f'Bearer {self.token}'})
        if test.status_code == 401:
            return False
        else:
            return True

    def __repr__(self):
        return f'<SynergiaAuthSession for {self.name} {self.surname} based on token {self.token}>'

    def __str__(self):
        return f'Auth session for {self.name} {self.surname}'


def oauth_librus_code(email, passwd, revalidation=False):
    if revalidation:
        mini_session = auth_session.get(LIBRUSLOGINURL, allow_redirects=False)
        access_code = mini_session.headers['location'][26:]
        return access_code
    else:
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
        raise exeptions.LibrusLoginError('Zły login lub hasło lub inny błąd związany z autoryzacją')

    redir_addr = login_response_redir.json()['redirect']
    access_code = auth_session.get(redir_addr, allow_redirects=False).headers['location'][26:]
    return access_code


def get_synergia_token(auth_code):
    return auth_session.post(
        OAUTHURL,
        data={
            'grant_type': 'authorization_code',
            'code': auth_code,
            'client_id': CLIENTID,
            'redirect_uri': REDIRURI
        }
    ).json()['access_token']


def try_to_fetch_logins(access_token, print_requests=False, connecting_tries=10):
    try:
        for connection_try in range(0, connecting_tries):
            try:
                response = auth_session.get(
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
        raise exeptions.LibrusNotHandlerableError('Serwer librusa ma problem z prostymi zapytaniami...')


def get_avaiable_users(access_token, print_credentials=False):
    accounts = try_to_fetch_logins(access_token)
    users = []
    for d in accounts:
        if print_credentials:
            print(json.dumps(d))
        users.append(SynergiaAuthSession(d))
    return users


def get_new_token(login, email, passwd):
    auth_session.get(
        FRESHURL.format(login=login)
    )
    return get_synergia_token(oauth_librus_code(email, passwd, revalidation=True))


def aio(email, passwd, fetch_index=0):
    oauth_code = oauth_librus_code(email, passwd)
    synergia_token = get_synergia_token(oauth_code)
    api_users = get_avaiable_users(synergia_token)
    u = api_users[fetch_index]
    if not u.is_authenticated:
        synergia_token = get_new_token(u.login, email, passwd)
        api_users = get_avaiable_users(synergia_token)
        u = api_users[fetch_index]
    return u
