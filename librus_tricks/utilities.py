from librus_tricks.classes import SynergiaAttendance, SynergiaAttendanceType, SynergiaGrade, SynergiaGlobalClass, \
    SynergiaVirtualClass, SynergiaLesson, SynergiaSubject, SynergiaTeacher, SynergiaExam
from datetime import datetime


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


def get_all_absence_types(session):
    non_present_types_raw = get_objects(session, 'Attendances/Types', '', 'Types', SynergiaAttendanceType)
    non_present_types = set()
    for t in non_present_types_raw:
        if not t.is_presence_kind:
            non_present_types.add(t)

    return tuple(non_present_types)


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
    :rtype: dict
    """

    def _define_group_and_type(payload):
        """

        :param dict payload:
        :return:
        """
        if 'VirtualClass' in payload.keys():
            return {'Id': payload['VirtualClass']['Id'], 'type': SynergiaVirtualClass}
        elif 'Class' in payload.keys():
            return {'Id': payload['Class']['Id'], 'type': SynergiaGlobalClass}
        else:
            raise AttributeError('Wrong object type')

    def _select_classroom(payload):
        if 'Classroom' in payload.keys():
            return payload['Classroom']['Id']
        elif 'OrgClassroom' in payload.keys():
            return payload['OrgClassroom']['Id']
        else:
            return None

    class TimetableFrame:
        def __init__(self, lesson_payload, session):
            self._session = session

            class ObjectsIds:
                def __init__(self, group_id, group_type, classroom_id, lesson_id, subject_id, teacher_id, timetable_entry):
                    self.group = group_id
                    self.group_type = group_type
                    self.classroom = classroom_id
                    self.lesson = lesson_id
                    self.subject = subject_id
                    self.teacher = teacher_id
                    self.timetable_entry = timetable_entry

            class ObjectsPreview:
                def __init__(self, teacher_name, teacher_lastname, subject_name):
                    self.teacher_name = teacher_name
                    self.teacher_lastname = teacher_lastname
                    self.subject_name = subject_name

            self.start = datetime.strptime(lesson_payload['HourFrom'], '%H:%M').time()
            self.end = datetime.strptime(lesson_payload['HourTo'], '%H:%M').time()
            self.is_canceled = lesson_payload['IsCanceled']
            self.is_substitution = lesson_payload['IsSubstitutionClass']
            self.lesson_no = int(lesson_payload['LessonNo'])
            self.preloaded_data = ObjectsPreview(
                lesson_payload['Teacher']['FirstName'],
                lesson_payload['Teacher']['LastName'],
                lesson_payload['Subject']['Name']
            )
            self.objects_ids = ObjectsIds(
                _define_group_and_type(lesson_payload)['Id'],
                _define_group_and_type(lesson_payload)['type'],
                _select_classroom(lesson_payload),
                lesson_payload['Lesson']['Id'],
                lesson_payload['Subject']['Id'],
                lesson_payload['Teacher']['Id'],
                lesson_payload['TimetableEntry']['Id']
            )

        @property
        def group(self):
            if self.objects_ids.group_type is SynergiaGlobalClass:
                return session.csync(self.objects_ids.group, SynergiaGlobalClass)
            else:
                return session.csync(self.objects_ids.group, SynergiaVirtualClass)

        # @property
        # def classroom(self):
        #     return  # TODO: Dodać klasę w classes.py

        @property
        def lesson(self):
            return SynergiaLesson(self.objects_ids.lesson, self._session)

        @property
        def subject(self):
            return self._session.csync(self.objects_ids.subject, SynergiaSubject)

        @property
        def teacher(self):
            return self._session.csync(self.objects_ids.teacher, SynergiaTeacher)

        def __repr__(self):
            return f'<TimetableFrame {self.start.strftime("%H:%M")}->{self.end.strftime("%H:%M")} {self.preloaded_data.subject_name} with {self.preloaded_data.teacher_name} {self.preloaded_data.teacher_lastname }>'

    if week_start == None:
        timetable_raw = session.get('Timetables')['Timetable']
    else:
        timetable_raw = session.get('Timetables', request_params={'weekStart': week_start})['Timetable']
    ordered_table = dict()
    for day in timetable_raw.keys():
        for frame in timetable_raw[day]:
            for lesson in frame:
                if not (day in ordered_table.keys()):
                    ordered_table[day] = []
                ordered_table[day].append(
                    TimetableFrame(lesson, session)
                )

    return ordered_table


def get_exams(session, *selected_calendars):
    """

    :param librus_tricks.core.SynergiaClient session: obiekt sesji z API Synergii
    :param selected_calendars:
    :return:
    """
    exams = []
    if selected_calendars.__len__() == 0:
        selected_calendars = [x['Id'] for x in session.get('Calendars')['Calendars']]
    for cal in selected_calendars:
        raw_exams = session.get('Calendars', cal)['Calendar']['HomeWorks']
        cal_exams = [SynergiaExam(x['Id'], session) for x in raw_exams]
        for e in cal_exams:
            exams.append(e)
    return exams
