from .generic_types import *


class SynergiaGrade:
    def __init__(self, grade_dict, session, get_extra_info=False):
        self.synergia_session = session
        self.grade = grade_dict['Grade']
        self.date = datetime.datetime.strptime(grade_dict['AddDate'], '%Y-%m-%d %H:%M:%S')
        self.semester = grade_dict['Semester']
        self.is_constituent = grade_dict['IsConstituent']
        self.is_semester_grade = grade_dict['IsSemester']
        self.id_semester_grade_prop = grade_dict['IsSemesterProposition']
        self.is_final_grade = grade_dict['IsFinal']
        self.is_final_grade_prop = grade_dict['IsFinalProposition']
        self.lesson = SynergiaLesson(grade_dict['Lesson']['Id'], self.synergia_session, False)
        self.subject = SynergiaSubject(grade_dict['Subject']['Id'], self.synergia_session, False)
        self.student = SynergiaTeacher(grade_dict['Student']['Id'], self.synergia_session,
                                       False)  # TODO: poprawić nazewnictwo
        # self.category = SynergiaLesson(grade_dict['Category']['Id'], self.synergia_session, False) # TODO: stworzyć klasę
        self.added_by = SynergiaTeacher(grade_dict['AddedBy']['Id'], self.synergia_session, False)

        if get_extra_info:
            self.get_extra_info()
            self.have_extra = True
        else:
            self.have_extra = False

    def get_extra_info(self):
        self.lesson.get_extra_info()
        self.subject.get_extra_info()
        self.student.get_extra_info()
        # self.category.get_extra_info()
        self.added_by.get_extra_info()

    def __repr__(self):
        return f'<{self.__class__.__name__} "{self.grade}" for subject {self.subject} added ' \
            f'{self.date.strftime("%Y-%m-%d %H:%M:%S")}>'


class SynergiaTimetableEntry:
    def __init__(self, entry_dict, session, collect_extra=False):
        """

        :param entry_dict:
        :type entry_dict: dict
        :param session:
        :param collect_extra:
        """
        self.synergia_session = session
        self.lesson = SynergiaLesson(entry_dict['Lesson']['Id'], self.synergia_session, get_extra_info=collect_extra)
        if 'Classroom' in entry_dict.keys():
            self.classroom = SynergiaClassroom(entry_dict['Classroom']['Id'], self.synergia_session,
                                               get_extra_info=collect_extra)
        else:
            self.classroom = SynergiaClassroom(entry_dict['OrgClassroom']['Id'], self.synergia_session,
                                               get_extra_info=collect_extra)
        self.lesson_entry = SynergiaLessonEntry(entry_dict['TimetableEntry']['Id'], self.synergia_session,
                                                get_extra_info=collect_extra)
        self.day_no = entry_dict['DayNo']
        self.subject = SynergiaSubject(entry_dict['Subject']['Id'], self.synergia_session, get_extra_info=collect_extra)
        self.teacher = SynergiaTeacher(entry_dict['Teacher']['Id'], self.synergia_session, get_extra_info=collect_extra)
        self.is_substitution_lesson = entry_dict['IsSubstitutionClass']
        self.is_canceled = entry_dict['IsCanceled']
        self.substitution_desc = entry_dict['SubstitutionNote']
        self.hour_from = entry_dict['HourFrom']  # TODO: zmienić na obiekt typu datetime
        self.hour_to = entry_dict['HourTo']
        if 'VirtualClass' in entry_dict.keys():
            self.virtual_class = SynergiaVirtualClass(entry_dict['VirtualClass']['Id'], self.synergia_session,
                                                      get_extra_info=collect_extra)
        else:
            self.virtual_class = None

    def __repr__(self):
        return f'<SynergiaTimetableEntry between {self.hour_from}-{self.hour_to}>'