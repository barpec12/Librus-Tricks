from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from .exceptions import *

# Some globals
REDIRURL = 'http://localhost/bar'
LOGINURL = 'https://portal.librus.pl/rodzina/login/action'
OAUTHURL = 'https://portal.librus.pl/oauth2/access_token'
SYNERGIAAUTHURL = 'https://portal.librus.pl/api/v2/SynergiaAccounts'
FRESHURL = 'https://portal.librus.pl/api/v2/SynergiaAccounts/fresh/{login}'
CLIENTID = 'wmSyUMo8llDAs4y9tJVYY92oyZ6h4lAt7KCuy0Gv'
LIBRUSLOGINURL = f'https://portal.librus.pl/oauth2/authorize?client_id={CLIENTID}&redirect_uri={REDIRURL}&response_type=code'


class SynergiaUser:
    def __init__(self, user_dict, root_token, revalidation_token, exp_in):
        self.token = user_dict['accessToken']
        self.refresh_token = revalidation_token
        self.root_token = root_token
        self.name, self.last_name = user_dict['studentName'].split(' ')
        self.login = user_dict['login']
        self.uid = user_dict['id']
        self.expires_in = datetime.now() + timedelta(seconds=exp_in)

    def __repr__(self):
        return f'<SynergiaUser for {self.name} {self.last_name} based on ' \
               f'token {self.token[:6] + "..." + self.token[-6:]}>'

    def __str__(self):
        return f'{self.name} {self.last_name}'

    def revalidate_root(self):
        auth_session = requests.session()
        new_tokens = auth_session.post(
            OAUTHURL,
            data={
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': CLIENTID
            }
        )
        self.root_token = new_tokens.json()['access_token']
        self.refresh_token = new_tokens.json()['refresh_token']

    def revalidate_user(self):
        auth_session = requests.session()
        new_token = auth_session.get(
            FRESHURL.format(login=self.login),
            headers={'Authorization': f'Bearer {self.root_token}'}
        )
        self.token = new_token.json()['accessToken']

    def is_revalidation_required(self, use_clock=True, use_query=False):
        clock_resp = None
        query_resp = None

        if use_clock:
            if datetime.now() > self.expires_in:
                clock_resp = False
            else:
                clock_resp = True
        if use_query:
            test = requests.get('https://api.librus.pl/2.0/Me', headers={'Authorization': f'Bearer {self.token}'})
            if test.status_code == 401:
                query_resp = False
            else:
                query_resp = True

        return clock_resp, query_resp


def authorizer(email, password):
    """
    Zwraca listę użytkowników dostępnych dla danego konta Librus Portal

    :param str email:
    :param str password:
    :return:
    :rtype: list of SynergiaUser
    """
    auth_session = requests.session()
    site = auth_session.get(LIBRUSLOGINURL)
    soup = BeautifulSoup(site.text, 'html.parser')
    csrf = soup.find('meta', attrs={'name': 'csrf-token'})['content']
    login_response_redirection = auth_session.post(
        LOGINURL, json={'email': email, 'password': password},
        headers={'X-CSRF-TOKEN': csrf, 'Content-Type': 'application/json'}
    )

    if login_response_redirection.status_code != 200:
        if login_response_redirection.status_code == 403:
            raise LibrusInvalidPasswordError(login_response_redirection.text)
        else:
            raise LibrusLoginError(login_response_redirection.text)

    redirection_addr = login_response_redirection.json()['redirect']
    redirection_response = auth_session.get(redirection_addr, allow_redirects=False)
    oauth_code = redirection_response.headers['location'].replace('http://localhost/bar?code=', '')

    synergia_root_response = auth_session.post(
        OAUTHURL,
        data={
            'grant_type': 'authorization_code',
            'code': oauth_code,
            'client_id': CLIENTID,
            'redirect_uri': REDIRURL
        }
    )
    synergia_root_login_token = synergia_root_response.json()['access_token']
    synergia_root_revalidation_token = synergia_root_response.json()['refresh_token']
    synergia_root_expiration = synergia_root_response.json()['expires_in']

    synergia_users_response = auth_session.get(SYNERGIAAUTHURL,
                                               headers={'Authorization': f'Bearer {synergia_root_login_token}'})
    synergia_users_raw = synergia_users_response.json()['accounts']
    synergia_users = [
        SynergiaUser(user_data, synergia_root_login_token, synergia_root_revalidation_token, synergia_root_expiration)
        for user_data in synergia_users_raw]
    return synergia_users
