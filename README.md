# LibrusTricks
Simple wrapper for Librus Synergia API written in Python

## Examples
```python
# Auth
from librus_tricks import ez_login, SynergiaSession
user = ez_login('krystian@postek.eu', 'not my real password')[0]
session = SynergiaSession(user)

# Get all grades
session.get_grades()
# {37664: [<SynergiaGrade "5-" for subject <SynergiaSubject with object id 37664> added 2018-10-17 13:26:37>, <SynergiaGrade "5-" for subject <SynergiaSubject with object id 37664> added 2018-10-17 13:37:37>, <SynergiaGrade "5-" for subject <SynergiaSubject with object id 37664> added 2018-11-21 14:15:14>, <SynergiaGrade "6" for subject <SynergiaSubject with object id 37664> added 2018-12-04 14:24:35>, <SynergiaGrade "5" for subject <SynergiaSubject with object id 37664> added 2018-12-12 14:26:25>, <SynergiaGrade "5" for subject <SynergiaSubject with object id 37664> added 2018-12-12 14:51:16>], 37678: [<SynergiaGrade "5" for subject <SynergiaSubject with object id 37678> added 2018-09-18 09:41:35>, <SynergiaGrade "4" for subject <SynergiaSubject with object id 37678> added 2018-10-12 13:42:50>, <SynergiaGrade "3" for subject <SynergiaSubject with object id 37678> added 2018-10-19 09:41:05>, <SynergiaGrade "5" for subject <SynergiaSubject with object id 37678> added 2018-10-30 09:39:39>, <SynergiaGrade "6" for subject <SynergiaSubject with object id 37678> added 2018-11-23 08:52:08>, <SynergiaGrade "5" for subject <SynergiaSubject with object id 37678> added 2018-12-18 09:44:15>], 37668: [<SynergiaGrade "+" for subject <SynergiaSubject with object id 37668> added 2018-09-19 10:14:01>, <SynergiaGrade "3" for subject <SynergiaSubject with object id 37668> added 2018-09-24 14:32:25>, <SynergiaGrade "4" for subject <SynergiaSubject with object id 37668> added 2018-10-25 08:40:23>, <SynergiaGrade "3" for subject <SynergiaSubject with object id 37668> added 2018-10-29 13:17:44>...

# Get timetable
session.get_timetable()
# {'2018-12-31': [], '2019-01-01': [], '2019-01-02': [<SynergiaTimetableEntry between 08:55-09:40>, <SynergiaTimetableEntry between 09:50-10:35>, <SynergiaTimetableEntry between 10:50-11:35>...

# Get lucky number
session.get_lucky_num()
# {'LuckyNumber': 12, 'LuckyNumberDay': '2018-12-22'}

```

## Screens from debugger
![screen](https://github.com/Backdoorek/public-files/raw/master/pycharm64_2018-12-28_14-08-37.png)

> Written with ❤ from scratch by Krystian `Backdoorek` Postek 