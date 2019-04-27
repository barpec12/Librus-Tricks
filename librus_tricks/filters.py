def filter_grades(grades, semesters=(1, 2), grade_type='partial'):
    """

    :type grades: list of librus_tricks.classes.SynergiaGrade
    """
    grades = [g for g in grades if g.semester in semesters]

    if grade_type == 'partial':
        grades = [g for g in grades if g.metadata.is_constituent]
    elif grade_type == 'final':
        grades = [g for g in grades if g.metadata.is_final_grade is True or g.metadata.is_semester_grade is True]
    elif grade_type == 'proposition':
        grades = [g for g in grades if
                  g.metadata.is_final_grade_proposition is True or g.metadata.is_semester_grade_proposition is True]
    else:
        raise Exception('Invalid type')

    return grades


def categorize_grades(grades):
    """

    :type grades: list of librus_tricks.classes.SynergiaGrade
    """
    grades_dict = dict()

    for grade in grades:
        if grade.subject not in grades_dict.keys():
            grades_dict[grade.subject] = []
        grades_dict[grade.subject].append(
            grade
        )

    return grades_dict


def categorize_attendance(attendances):
    """

    :type attendances: list of librus_tricks.classes.SynergiaAttendance
    """
    attendance_dict = dict()

    for att in attendances:
        if att.type not in attendance_dict.keys():
            attendance_dict[att.type] = []
        attendance_dict[att.type].append(
            att
        )

    return attendance_dict
