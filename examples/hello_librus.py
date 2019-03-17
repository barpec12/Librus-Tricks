from librus_tricks.auth import aio
import getpass
from colorama import Fore, init as colorama_init


def ask_for_credentials():
    login = input('E-mail: ')
    passwd = getpass.getpass('Passwd: ')
    return {'email': login, 'passwd': passwd}


if __name__ == '__main__':
    colorama_init(autoreset=True)
    print(Fore.BLUE + 'Logging in')
    user = aio(**ask_for_credentials())
    print(Fore.CYAN + 'Checking user auth')
    if user.is_authenticated:
        print(Fore.GREEN + 'Authenticated')
    else:
        print(Fore.RED + 'Unauthenticated')
