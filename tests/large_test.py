import os
import sys
import requests

sys.path.extend(['./'])

email = os.environ['librus_email']
password = os.environ['librus_password']

from librus_tricks import aio, SynergiaClient

# Trying to handle strange pytest errors/bugs
try:
    session = SynergiaClient(aio(email, password), cache_location=':memory:')
except KeyError:
    session = SynergiaClient(aio(email, password, force_revalidation_method=True), cache_location=':memory:')
except requests.exceptions.ConnectionError:
    session = SynergiaClient(aio(email, password, force_revalidation_method=True), cache_location=':memory:')


def test_grades():
    grade = session.get_grades()
    teachers = []
    subjects = []
    comments = []
    categories = []
    for g in grade:
        teachers.append(
            g.teacher
        )
        if not g.subject == None:
            subjects.append(
                g.subject
            )
        subjects.append(
            g.comments
        )
        categories.append(
            g.category
        )

    return grade, teachers, subjects, comments, categories


def test_attendances():
    atts = session.get_attendances()
    teachers = []
    types = []
    for a in atts:
        teachers.append(
            a.teacher
        )
        types.append(
            a.type
        )

    return teachers, types


def test_exams():
    exams = session.get_exams()
    teachers = []
    subjects = []
    groups = []
    for e in exams:
        teachers.append(
            e.teacher
        )
        subjects.append(
            e.subject
        )
        groups.append(
            e.group
        )

    return teachers, subjects, groups

def test_timetable():
    week = session.get_timetable()
    subjects = []
    teachers = []
    lessons = []
    groups = []
    classrooms = []
    for day in week.keys():
        for frame in week[day]:
            subjects.append(
                frame.subject
            )
            teachers.append(
                frame.teacher
            )
            lessons.append(
                frame.lesson
            )
            groups.append(
                frame.group
            )
            classrooms.append(
                frame.classroom
            )

    return subjects, teachers, lessons, groups, classrooms
