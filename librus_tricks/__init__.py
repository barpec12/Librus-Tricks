name = 'librus_tricks'
__title__ = 'librus_tricks'
__author__ = 'Backdoorek'
__version__ = 'alpha-0.0.1'

from librus_tricks.auth import authorizer
from librus_tricks.core import SynergiaClient
from librus_tricks.classes import *


async def create_session(email, password) -> SynergiaClient:
    user = (await authorizer(email, password))[0]
    session = SynergiaClient(user)
    return session
