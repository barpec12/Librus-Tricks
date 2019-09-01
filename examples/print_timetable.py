import getpass
from datetime import datetime
from types import SimpleNamespace as Namespace

from colorama import init as colorama_init, Fore
from prettytable import PrettyTable

from librus_tricks import create_session


def ask_for_credentials():
    login = input('E-mail: ')
    passwd = getpass.getpass('Passwd: ')
    return {'email': login, 'password': passwd}


def max_lenght_of_ttc(dtc):
    lens = []
    for k in dtc.keys():
        lens.append(
            dtc[k].__len__()
        )
    return max(*lens)


def get_longest_ttc_ranges(dtc):
    max_len = 0
    output = []
    for k in dtc.keys():
        if dtc[k].__len__() > max_len:
            max_len = dtc[k].__len__()
            output = [(tte.start, tte.end) for tte in dtc[k]]
    return output


if __name__ == '__main__':
    colorama_init(autoreset=True)
    print(Fore.BLUE + 'Logging in...')
    session = create_session(**ask_for_credentials())


    class FakeTTE:
        def __init__(self):
            self.subject = Namespace()
            self.subject.name = ''
            self.subject.short_name = ''
            self.classroom = Namespace()
            self.classroom.symbol = ''


    tt = session.get_timetable()
    pt = PrettyTable()

    mlv = max_lenght_of_ttc(tt)

    for k in tt.keys():
        if tt[k].__len__() < mlv:
            for n in range(mlv - tt[k].__len__()):
                tt[k].append(FakeTTE())

    pt.add_column(
        '',
        [Fore.CYAN + f'{tter[0].strftime("%H:%M")} - {tter[1].strftime("%H:%M")}' + Fore.RESET for tter in
         get_longest_ttc_ranges(tt)]
    )
    for day in tt.keys():
        pt.add_column(
            datetime.strptime(day, '%Y-%m-%d').strftime(Fore.CYAN + '%A' + Fore.RESET),
            [f'{tte.subject.name}' for tte in tt[day] if tte]
        )

    print(pt)
