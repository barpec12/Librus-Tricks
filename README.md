<div align="center">
    <h1>Librus Tricks</h1>

[![Tests](https://img.shields.io/travis/Backdoorek/Librus-Tricks.svg?logo=travis&style=for-the-badge)](https://travis-ci.org/Backdoorek/Librus-Tricks)[![Codacy grade](https://img.shields.io/codacy/grade/afcbb085b8a746db8795c3a5a13054e6.svg?logo=codacy&style=for-the-badge)](https://app.codacy.com/project/Backdoorek/Librus-Tricks/dashboard)

[![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/Backdoorek/Librus-Tricks.svg?color=gray&logo=github&style=for-the-badge)![GitHub commit activity](https://img.shields.io/github/commit-activity/m/Backdoorek/Librus-Tricks.svg?style=for-the-badge)](https://github.com/Backdoorek/Librus-Tricks)

[![PyPI - Downloads](https://img.shields.io/pypi/dm/librus-tricks.svg?style=for-the-badge)![PyPI - Version](https://img.shields.io/pypi/v/librus-tricks.svg?style=for-the-badge)![PyPI - Python Version](https://img.shields.io/pypi/pyversions/librus-tricks.svg?style=for-the-badge)](https://pypi.org/project/librus-tricks/)

Fast and powerful Synergia Librus API wrapper
</div>

## What is inside the box?
 - Flexible cache system (Based on SQLAlchemy ORM)
 - Easy to use authentication process
 - Lazy object loading
 - Use features from `Mobilne Dodatki` or their spare solutions
 - `__repr__` and `__str__` are pretty human readable

## Install
```text
# Windows
# Latest stable
pip install librus-tricks
# Libs for examples
pip install librus-tricks[examples]
# Dev channel
pip install git+https://github.com/Backdoorek/Librus-Tricks.git@prototype

# Linux
# Latest stable
sudo -H pip3 install librus-tricks
# Libs for examples
sudo -H pip3 install librus-tricks[examples]
# Dev channel
sudo -H pip3 install git+https://github.com/Backdoorek/Librus-Tricks.git@prototype
```

## Examples
```python
# Create session (with support for messages, require the same password for Portal Librus and Synergia)
from librus_tricks import create_session
session = create_session('my@email.com', 'admin1')

# If passwords are different
from librus_tricks import SynergiaClient, authorizer
session = SynergiaClient(authorizer('my@email.com', 'admin1')[0], synergia_user_passwd='admin2')

# Get selected grades
session.get_grades(selected=(27208160, 24040273, 21172894))
# (<SynergiaGrade 21172894>, <SynergiaGrade 24040273>, <SynergiaGrade 27208160>)

# Get future exams
session.get_exams()
# [<SynergiaExam 2019-03-27 00:00:00 for subject with id 37659>, <SynergiaExam 2019-03-28 00:00:00 for subject with id 37675>, <SynergiaExam 2019-03-26 00:00:00 for subject with id 37670>]

# Get timetable
session.get_timetable()
# {'2019-03-18': [<TimetableFrame 08:00->08:45 Historia with Krzysztof ...>, <TimetableFrame 08:55->09:40 Wychowanie fizyczne with Artur ...>, <TimetableFrame 09:50->10:35 Wychowanie fizyczne with Arkadiusz ...>, <TimetableFrame 10:50->11:35 Edukacja dla bezpieczeństwa with Arkadiusz ...>, <TimetableFrame 11:45->12:30 Godzina wychowawcza with Elżbieta ...>, <TimetableFrame 12:50->13:35 Język polski with Aleksandra ...>, <TimetableFrame 13:50->14:35 Język polski with Aleksandra ...>], '2019-03-19': [<TimetableFrame 08:00->08:45 Matematyka with Joanna ...>, <TimetableFrame 08:55->09:40 Matematyka with Joanna ...>, <TimetableFrame 09:50->10:35 Geografia with Agnieszka ...>, <TimetableFrame 10:50->11:35 Wiedza o społeczeństwie with Sylwia ...>, <TimetableFrame 11:45->12:30 Język niemiecki with Elżbieta ...>, <TimetableFrame 12:50->13:35 Matematyka with Joanna ...>], '2019-03-20': [<TimetableFrame 08:00->08:45 Chemia with Edyta ...>, <TimetableFrame 08:55->09:40 Religia with Magdalena ...>, <TimetableFrame 09:50->10:35 Język angielski with Krystyna ...>, <TimetableFrame 10:50->11:35 Etyka with Marta ...>, <TimetableFrame 11:45->12:30 Informatyka with Iwona ...>, <TimetableFrame 12:50->13:35 Język angielski with Krystyna ...>, <TimetableFrame 13:50->14:35 Język niemiecki with Elżbieta ...>], '2019-03-21': [<TimetableFrame 08:00->08:45 Język polski with Aleksandra ...>, <TimetableFrame 08:55->09:40 Język polski with Aleksandra ...>, <TimetableFrame 09:50->10:35 Fizyka with Hieronim ...>, <TimetableFrame 10:50->11:35 Wiedza o kulturze with Elżbieta ...>, <TimetableFrame 11:45->12:30 Religia with Magdalena ...>, <TimetableFrame 12:50->13:35 Język angielski with Krystyna ...>, <TimetableFrame 13:50->14:35 Język angielski with Krystyna ...>], '2019-03-22': [<TimetableFrame 08:00->08:45 Wychowanie fizyczne with Arkadiusz ...>, <TimetableFrame 08:55->09:40 Wychowanie fizyczne with Arkadiusz ...>, <TimetableFrame 09:50->10:35 Informatyka with Iwona ...>, <TimetableFrame 10:50->11:35 Matematyka with Joanna ...>, <TimetableFrame 11:45->12:30 Matematyka with Joanna ...>]}

# Get messages
session.message_reader.read_messages()
# [<Message from aaa Izabella (aaa Izabella) into /wiadomosci/1/5/5983071/f0>, ...]
```

For more examples check the [examples](https://github.com/Backdoorek/Librus-Tricks/tree/prototype/examples) folder

## Gallery
![](https://github.com/Backdoorek/public-files/blob/master/Z270-HD3P_2019-05-18_09'23'03.png?raw=true)
![](https://github.com/Backdoorek/public-files/blob/master/Discord_2019.05.01_130054.png?raw=true)
![](https://github.com/Backdoorek/public-files/blob/master/Discord_2019.05.01_133954.png?raw=true)

> Written with ❤ from a scratch by Krystian _`Backdoorek`_ Postek
>
> Thanks for guys from [librus-client](https://discord.gg/ybTX4gM) for help with getting into it
