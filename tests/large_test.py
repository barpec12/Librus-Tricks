import os
import sys
import requests

sys.path.extend(['./'])

email = os.environ['librus_email']
password = os.environ['librus_password']

from librus_tricks import aio, SynergiaClient, utilities

# Trying to handle strange pytest errors/bugs
try:
    session = SynergiaClient(aio(email, password), cache_location=':memory:', synergia_user_passwd=password)
except KeyError:
    session = SynergiaClient(aio(email, password, force_revalidation_method=True), cache_location=':memory:', synergia_user_passwd=password)
except requests.exceptions.ConnectionError:
    session = SynergiaClient(aio(email, password, force_revalidation_method=True), cache_location=':memory:', synergia_user_passwd=password)


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
        if not g.subject is None:
            subjects.append(
                g.subject
            )
        subjects.append(
            g.comments
        )
        categories.append(
            g.category
        )

    print(*teachers)
    print(*subjects)
    print(*comments)
    print(*categories)
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

    print(*teachers)
    print(*types)
    return teachers, types


def test_exams():
    exams = session.get_exams()
    teachers = []
    subjects = []
    groups = []
    cats = []
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
        cats.append(
            e.category
        )

    print(*subjects)
    print(*teachers)
    print(*groups)
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

    print(*subjects)
    print(*teachers)
    print(*lessons)
    print(*groups)
    print(*classrooms)
    return subjects, teachers, lessons, groups, classrooms


def test_newsfeed():
    feed = session.get_news()
    teachers = []
    for n in feed:
        teachers.append(
            n.teacher
        )

    print(*teachers)
    return teachers


def test_freedays():
    teacherss = []
    for_all = []
    for f in utilities.get_teachers_free_days(session, False):
        teacherss.append(
            f
        )
        teacherss.append(
            f.teacher
        )
    for f in utilities.get_free_days(session, False):
        for_all.append(
            f
        )

    print(*teacherss)
    print(*for_all)
    return teacherss, for_all
