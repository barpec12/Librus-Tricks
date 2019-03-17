from librus_tricks.types import SynergiaAttendance, SynergiaAttendanceType, SynergiaGrade


def get_all_grades(session):
    """

    :type session: librus_tricks.core.SynergiaClient
    """
    grades_raw = session.get('Grades')['Grades']
    grades_list = []
    for record in grades_raw:
        grades_list.append(
            SynergiaGrade(record['Id'], session, payload=record)
        )
    return tuple(grades_list)


def get_all_attendance(session):
    """

    :type session: librus_tricks.core.SynergiaClient
    """
    attendance_raw = session.get('Attendances')['Attendances']
    attendance_list = []
    for record in attendance_raw:
        attendance_list.append(
            SynergiaAttendance(record['Id'], session, payload=record)
        )
    return tuple(attendance_list)


def get_all_attendance_types(session):
    """

    :type session: librus_tricks.core.SynergiaClient
    """
    a_types_raw = session.get('Attendances', 'Types')['Types']
    a_types_set = set()
    for t in a_types_raw:
        a_types_set.add(
            SynergiaAttendanceType(t['Id'], session, t)
        )
    return a_types_set


def get_filtered_attendance(session, *a_types):
    """

    :type session: librus_tricks.core.SynergiaClient
    """
    attendance_raw = session.get('Attendances')['Attendances']
    attendance_list = []
    allowed_types = set()

    for t in a_types:
        allowed_types.add(
            t.oid
        )

    for record in attendance_raw:
        if record['Type']['Id'] in allowed_types:
            attendance_list.append(
                SynergiaAttendance(record['Id'], session, payload=record)
            )

    return attendance_list


def get_objects(session, path_computed, ids_computed, extraction_key, cls):
    """

    :type session: librus_tricks.core.SynergiaClient
    """
    response = session.get(path_computed, ids_computed)[extraction_key]
    objects = []
    for i in response:
        objects.append(
            cls(i['Id'], session, payload=i)
        )
    return tuple(objects)
