import os
import sys

sys.path.extend(['./'])

email = os.environ['librus_email']
password = os.environ['librus_password']

from librus_tricks import exceptions, create_session

session = create_session(email, password, cache_location=':memory:')


def test_auth():
    return session.user.is_revalidation_required(use_query=True)


def test_attendance():
    return session.get_attendances()


def test_exams():
    return session.get_exams()


def test_grades():
    return session.get_grades()


def test_timetable():
    try:
        return session.get_timetable()
    except exceptions.SynergiaAccessDenied as err:
        return str(err)


def test_newsfeed():
    return session.get_news()


def test_messages():
    return session.message_reader.read_messages()


def test_basetextgrades():
    return session.get_basetextgrades()
