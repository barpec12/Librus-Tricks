# This example require:
# login.json
# {
#   "email": "your@mail.com",
#   "passwd": "Your damn pass"
# }`

import json
from librus_tricks import ez_login, SynergiaSession, convert_grade_keys

conf = json.load(open('login.json', mode='r'))
user = ez_login(conf['email'], conf['passwd'])[0]
session = SynergiaSession(user)
grades = convert_grade_keys(session.get_grades(), session)

if __name__ == '__main__':
    for k in grades.keys():
        gs = [a.grade for a in grades[k] if not (a.is_semester_grade or a.id_semester_grade_prop or a.is_final_grade or a.is_final_grade_prop)]
        print(k.name + ':', *gs)
        print('----')
