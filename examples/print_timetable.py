import getpass

from colorama import init as colorama_init, Fore

from librus_tricks import utilities, aio, SynergiaClient


def ask_for_credentials():
    login = input('E-mail: ')
    passwd = getpass.getpass('Passwd: ')
    return {'email': login, 'passwd': passwd}


if __name__ == '__main__':
    colorama_init(autoreset=True)
    print(Fore.BLUE + 'Logging in...')
    session = SynergiaClient(aio(**ask_for_credentials()))
    tt = utilities.get_timetable(session)
    for day in tt.keys():
        print(Fore.MAGENTA + day)
        for frame in tt[day]:
            if frame.is_substitution:
                print(
                    Fore.BLUE + f'{frame.start.strftime("%H:%M")}->{frame.end.strftime("%H:%M")} '
                    f'- {frame.preloaded_data.subject_name} '
                    f'z {frame.preloaded_data.teacher_name} {frame.preloaded_data.teacher_lastname} (zastępstwo)')
            else:
                print(
                    Fore.CYAN + f'{frame.start.strftime("%H:%M")}->{frame.end.strftime("%H:%M")} '
                    f'- {frame.preloaded_data.subject_name} '
                    f'z {frame.preloaded_data.teacher_name} {frame.preloaded_data.teacher_lastname}')
