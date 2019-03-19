from librus_tricks import utilities, aio, SynergiaClient
import getpass
from colorama import init as colorama_init, Fore


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
        print(Fore.GREEN + day)
        for frame in tt[day]:
            print(
                Fore.CYAN + f'{frame.start.strftime("%H:%M")}->{frame.end.strftime("%H:%M")} - {frame.preloaded_data.subject_name} z {frame.preloaded_data.teacher_name} {frame.preloaded_data.teacher_lastname}')
