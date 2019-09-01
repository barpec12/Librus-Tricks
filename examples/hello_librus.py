import getpass

from colorama import Fore, init as colorama_init

from librus_tricks.auth import aio, exceptions


def ask_for_credentials():
    login = input('E-mail: ')
    passwd = getpass.getpass('Passwd: ')
    return {'email': login, 'password': passwd, 'passwd': passwd}


if __name__ == '__main__':
    colorama_init(autoreset=True)
    print(Fore.BLUE + 'Logging in')
    try:
        user = aio(**ask_for_credentials())
    except exceptions.LibrusInvalidPasswordError:
        print(Fore.RED + 'Złe hasło')
        user = aio(**ask_for_credentials())
    print(Fore.CYAN + 'Checking user auth')
    if user.is_authenticated:
        print(Fore.GREEN + 'Authenticated')
    else:
        print(Fore.RED + 'Unauthenticated')
