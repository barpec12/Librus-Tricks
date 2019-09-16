import os
import sys

sys.path.extend(['./'])

email = os.environ['librus_email']
password = os.environ['librus_password']

from librus_tricks import create_session, cache

session = create_session(email, password, cache=cache.AlchemyCache(engine_uri='sqlite:///:memory:'))


def test_grade():
    grades = session.grades()
    teachers = [x.teacher for x in grades]
    subjects = [x.subject for x in grades]
    cats = [x.category for x in grades]
    return teachers, subjects, cats


def test_attedance():
    att = session.attendances()
    types = [x.type for x in att]
    return att, types
