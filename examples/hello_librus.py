from librus_tricks.auth import aio


def ask_for_credentials():
    login = input('E-mail: ')
    passwd = input('Passwd: ')
    return {'email': login, 'passwd': passwd}


if __name__ == '__main__':
    print('Logging in')
    user = aio(**ask_for_credentials())
    print('Checking user auth')
    if user.is_authenticated:
        print('Authenticated')
    else:
        print('Unauthenticated')
