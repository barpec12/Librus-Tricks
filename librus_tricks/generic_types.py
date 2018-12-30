from librus_tricks import ez_login
from librus_tricks.types import SynergiaSession, SynergiaGenericClass


class SynergiaLesson(SynergiaGenericClass):
    def __init__(self, obj_id, session, get_extra_info=False):
        super().__init__(obj_id, session, get_extra_info)

    def get_extra_info(self):
        print('Nadpisana')


if __name__ == '__main__':
    user = ez_login('krystian@postek.eu', '$Un10ck_lib')
    ss = SynergiaSession(user)
    sl = SynergiaLesson("1502496", ss, get_extra_info=True)
    print(sl)
