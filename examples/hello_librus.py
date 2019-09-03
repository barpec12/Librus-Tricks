import getpass

from colorama import Fore, init as colorama_init

from librus_tricks.auth import authorizer, SynergiaUser
from librus_tricks import exceptions


def ask_for_credentials():
    login = input('E-mail: ')
    passwd = getpass.getpass('Passwd: ')
    return {'email': login, 'password': passwd, 'passwd': passwd}


if __name__ == '__main__':
    colorama_init(autoreset=True)
    print(Fore.BLUE + 'Logging in')
    try:
        user: SynergiaUser = authorizer(**ask_for_credentials())[0]
    except exceptions.LibrusInvalidPasswordError:
        print(Fore.RED + 'Złe hasło')
        user: SynergiaUser = authorizer(**ask_for_credentials())[0]
    print(Fore.CYAN + 'Checking user auth')
    if user.is_revalidation_required(use_query=True):
        print(Fore.GREEN + 'Authenticated')
    else:
        print(Fore.RED + 'Unauthenticated')
