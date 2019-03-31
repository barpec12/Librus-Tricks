import os
import sys

sys.path.extend(['./'])

email = os.environ['librus_email']
password = os.environ['librus_password']

from librus_tricks import aio, SynergiaClient
import requests

# Trying to handle strange pytest errors/bugs
try:
    session = SynergiaClient(aio(email, password), cache_location=':memory:')
except KeyError:
    session = SynergiaClient(aio(email, password, force_revalidation_method=True), cache_location=':memory:')
except requests.exceptions.ConnectionError:
    session = SynergiaClient(aio(email, password, force_revalidation_method=True), cache_location=':memory:')


def test_auth():
    return session.user.is_authenticated


def test_attendance():
    return session.get_attendances()


def test_exams():
    return session.get_exams()


def test_grades():
    return session.get_grades()


def test_timetable():
    return session.get_timetable()


def test_newsfeed():
    return session.get_news()
