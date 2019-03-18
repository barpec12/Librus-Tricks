from librus_tricks.classes import SynergiaAttendance, SynergiaAttendanceType, SynergiaGrade


def get_all_grades(session):
    """
    Zwraca krotkę wszystkich ocen

    :param librus_tricks.core.SynergiaClient session: obiekt sesji z API Synergii
    :return: krotka z ocenami
    :rtype: tuple of librus_tricks.classes.SynergiaGrade
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
    Zwraca krotkę z całą frekwencją

    :param librus_tricks.core.SynergiaClient session: obiekt sesji z API Synergii
    :return: krotka z obecnościami
    :rtype: tuple of librus_tricks.SynergiaAttendance
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
    Zwraca krotkę wszystkich typów obecności.

    :param librus_tricks.core.SynergiaClient session: obiekt sesji z API Synergii
    :return: zbiór typów obecności
    :rtype: set of librus_tricks.classes.SynergiaAttendanceType
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
    Zwraca tylko wybrane typy obecności

    :param librus_tricks.core.SynergiaClient session: obiekt sesji z API Synergii
    :param librus_tricks.classes.SynergiaAttendanceType a_types: obiekty typów obecności
    :return: zbiór wybranych obecności
    :rtype: set of librus_tricks.classes.SynergiaAttendanceType
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
    Zwraca krotkę z obiektami danej klasy, na podstawie pełnego json'a

    :param librus_tricks.core.SynergiaClient session: obiekt sesji z API Synergii
    :param str path_computed: gotowa do wklejenia ścieżka
    :param str ids_computed: gotowe do wklejenia idiki
    :param str extraction_key: klucz to "wydłubania" danych
    :param any cls: klasa w którą ma zostać opakowany json
    :return: krotka wybranych obiektów klasy ``cls``
    :rtype: tuple
    """
    response = session.get(path_computed, ids_computed)[extraction_key]
    objects = []
    for i in response:
        objects.append(
            cls(i['Id'], session, payload=i)
        )
    return tuple(objects)

def get_timetable(session, week_start=None):
    """
    Zwraca uporządkowany plan lekcji

    :param librus_tricks.core.SynergiaClient session: obiekt sesji z API Synergii
    :param week_start: data poniedziałku dla wybranego tygodnia
    :return:
    """

    class ObjectsIds:
        def __init__(self, id_clss, clss_type, id_clsr, id_lesn, id_sub, id_tea, id_tte):
            self.group = id_clss
            self.group_type = clss_type
            self.classroom = id_clsr
            self.lesson = id_lesn,
            self.subject = id_sub,
            self.teacher = id_tea,
            self.timetable_entry = id_tte

    class ObjectsPreview:
        def __init__(self, teacher_name, teacher_lastname, subject_name):
            self.teacher_name = teacher_name
            self.teacher_lastname = teacher_lastname
            self.subject_name = subject_name

    class TimetableEntry:
        def __init__(self):
            pass

    class Timetable:
        def __init__(self, ordered_table):
            pass

    timetable_raw = session.get('Timetables')
    ordered_table = dict()
    for day in timetable_raw.keys():
        for frame in timetable_raw[day]:
            for lessons in frame:
                for lesson in lessons:
                    if not (day in ordered_table.keys()):
                        ordered_table[day] = []
                    ordered_table[day].append(

                    )


    return

if __name__ == '__main__':
    from librus_tricks import aio, SynergiaClient
    session = SynergiaClient(aio('krystian@postek.eu', '$Un10ck_lib'))
    get_timetable(session)
