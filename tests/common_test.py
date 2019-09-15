import os
import sys

sys.path.extend(['./'])

email = os.environ['librus_email']
password = os.environ['librus_password']

from librus_tricks import exceptions, create_session, cache

session = create_session(email, password, cache=cache.AlchemyCache(engine_uri='sqlite:///:memory:'))


def test_auth():
    return session.user.is_revalidation_required(use_query=True)


def test_attendance():
    return session.attendances()


def test_exams():
    return session.exams()


def test_grades():
    return session.grades()


def test_timetable():
    session.timetable()
    k = session.today_timetable
    return session.tomorrow_timetable


def test_newsfeed():
    return session.get_news()


def test_messages():
    return session.message_reader.read_messages()


def test_basetextgrades():
    return session.get_basetextgrades()


def test_colors():
    return session.colors()
