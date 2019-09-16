from librus_tricks import exceptions
from librus_tricks.auth import authorizer
from librus_tricks.classes import *
from librus_tricks.core import SynergiaClient

name = 'librus_tricks'
__title__ = 'librus_tricks'
__author__ = 'Backdoorek'
__version__ = '0.7.0'

def create_session(email, password, fetch_first=True, **kwargs):
    """
    Używaj tego tylko kiedy hasło do Portal Librus jest takie samo jako do Synergii

    :param email: str
    :param password: str
    :param fetch_first: bool or int
    :return:
    """
    if fetch_first is True:
        user = authorizer(email, password)[0]
        session = SynergiaClient(user, synergia_user_passwd=password, **kwargs)
        return session
    elif fetch_first is False:
        users = authorizer(email, password)
        sessions = [SynergiaClient(user, synergia_user_passwd=password, **kwargs) for user in users]
        return sessions
    else:
        user = authorizer(email, password)[fetch_first]
        session = SynergiaClient(user, synergia_user_passwd=password, **kwargs)
        return session