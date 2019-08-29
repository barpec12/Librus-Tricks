import getpass

from colorama import init as colorama_init, Fore

from librus_tricks import utilities, create_session, SynergiaAttendanceType


def ask_for_credentials():
    login = input('E-mail: ')
    passwd = getpass.getpass('Passwd: ')
    return {'email': login, 'passwd': passwd}


def create_name_dict(*a_types):
    names = dict()
    for a in a_types:
        names[a.oid.__str__()] = a.name
    return names


if __name__ == '__main__':
    colorama_init(autoreset=True)
    print(Fore.BLUE + 'Logging in...')
    session = create_session(**ask_for_credentials())
    attd_types = utilities.get_all_attendance_types(session)
    print(Fore.CYAN + 'Wybierz rodzaje obecności, które Cię interesują')
    for at in attd_types:
        print(Fore.CYAN + f'{at.name} ({at.short_name}) - {at.oid}')
    chosen = input('Podaj id\'ki (przedziel spacjami kolejne id\'ki): ').split(" ")
    req_types = [SynergiaAttendanceType(x, session) for x in chosen]
    chosen_name = create_name_dict(*req_types)
    attd_filt = utilities.get_filtered_attendance(session, *req_types)
    stats = dict()
    for a in attd_filt:
        if not (a.objects_ids.type.__str__() in stats.keys()):
            stats[a.objects_ids.type.__str__()] = 0
        stats[a.objects_ids.type.__str__()] += 1
        print(f'{a.type.short_name} - {a.date.strftime("%Y-%m-%d")} lekcja {a.lesson_no}')
    for stat in stats:
        print(f'{chosen_name[stat]} -> {stats[stat]}', end=' ')
