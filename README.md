# LibrusTricks
Simple wrapper for Librus Synergia API written in Python

## Examples
```python
from librus_tricks.utils import get_access_token, get_auth_code, get_synergia_users
from librus_tricks.types import SynergiaSession

# Auth
synergia_user = get_synergia_users(
    get_access_token(
        get_auth_code(
            'krystian@postek.eu', 'notmyrealpassword'    
    ))
)

# Create session
syn_sess = SynergiaSession(synergia_user)

# Get timetable
timetab_json = syn_sess.get_timetable(raw=True, week_start_str='2018-12-10') # As json (text)
timetab_dict = syn_sess.get_timetable(as_dict=True, week_start_str='2018-12-10') # As pythonic dict
timetab_py = syn_sess.get_timetable(week_start_str='2018-12-10') # Dict with interactive python objects

# Get grades
grades_json = syn_sess.get_grades(raw=True) # As json (text)
grades_dict = syn_sess.get_grades(as_dict=True) # As pythonic dict
```

![screen](https://github.com/Backdoorek/public-files/raw/master/pycharm64_2018-12-28_14-08-37.png)