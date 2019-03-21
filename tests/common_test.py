import os
import sys

sys.path.extend(['./'])

email = os.environ['librus_email']
password = os.environ['librus_password']

from librus_tricks import aio, SynergiaClient

session = SynergiaClient(aio(email, password))


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
