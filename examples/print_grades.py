import getpass

from colorama import Fore, init as colorama_init

from librus_tricks import create_session, SynergiaSubject


def ask_for_credentials():
    login = input('E-mail: ')
    passwd = getpass.getpass('Passwd: ')
    return {'email': login, 'passwd': passwd}


def sort_grades(session):
    """

    :type session: librus_tricks.core.SynergiaClient
    """
    obj_grades = session.get_grades()
    grades_sorted = {}
    grades = {}
    for g in obj_grades:
        grade_subject_id = g._json_payload['Subject']['Id']
        print(grade_subject_id)
        if not (str(grade_subject_id) in grades_sorted.keys()):
            print('Id not found')
            grades_sorted[str(grade_subject_id)] = []
        else:
            print('Id found')
        grades_sorted[str(grade_subject_id)].append(g)
        print(grades_sorted[str(grade_subject_id)])
    for key in grades_sorted.keys():
        grades[SynergiaSubject(key, session)] = grades_sorted[key]
    return grades


if __name__ == '__main__':
    colorama_init(autoreset=True)
    print(Fore.CYAN + 'Logging in...')
    session = create_session(**ask_for_credentials())
    print(Fore.CYAN + 'Printing user\'s grades')
    gs = sort_grades(session)
    for subject in gs.keys():
        print(Fore.MAGENTA + subject.name + ':')
        for grade in gs[subject]:
            if grade.metadata.is_constituent:
                category = grade.category
                print(Fore.BLUE + f'    {grade.grade} with category {category.name} ({category.weight}) @ {grade.date}')
