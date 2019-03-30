# LibrusTricks

[![Tests](https://img.shields.io/travis/Backdoorek/Librus-Tricks.svg?logo=travis&style=for-the-badge)](https://travis-ci.org/Backdoorek/Librus-Tricks)![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/Backdoorek/Librus-Tricks.svg?color=gray&logo=git&style=for-the-badge)![Implementation](https://img.shields.io/pypi/implementation/librus-tricks.svg?logo=python&logoColor=yellow&style=for-the-badge)

![PyPI - Downloads](https://img.shields.io/pypi/dm/librus-tricks.svg?style=for-the-badge)![PyPI - Version](https://img.shields.io/pypi/v/librus-tricks.svg?style=for-the-badge)


A powerful python Librus Synergia API based on RE

## Polaczków szukających szczegółów zapraszam [tutaj](https://github.com/Backdoorek/Librus-Tricks/wiki)

## What is inside the box?
 - Caching system (based on SQLite)
 - Lazy object loading
 - Simplified objects
 - Errors handlers
 - All-In-One login mechanism
 - Many buitt-in solutions (get future exams, get timetable etc.)
 - Docstrings (help for PyCharm, VS Codem, IDLE etc.)

## Install
```text
# Windows
# Latest stable
pip install librus-tricks
# Latest sources
pip install git+https://github.com/Backdoorek/Librus-Tricks.git@prototype

# Linux
# Latest stable
sudo -H pip3 install librus-tricks
# Latest sources
sudo -H pip3 install git+https://github.com/Backdoorek/Librus-Tricks.git@prototype
```

## Examples
```python
# Authentication
from librus_tricks import auth
user = auth.aio('my.mail@mydoamin.com', 'uniqepass')

# Create session
from librus_tricks import SynergiaClient
session = SynergiaClient(user)

# Get selected grades
session.get_grades(selected=('27208160', '24040273', '21172894'))
# (<SynergiaGrade 21172894>, <SynergiaGrade 24040273>, <SynergiaGrade 27208160>)

# Get future exams
session.get_future_exams()
# [<SynergiaExam 2019-03-27 00:00:00 for subject with id 37659>, <SynergiaExam 2019-03-28 00:00:00 for subject with id 37675>, <SynergiaExam 2019-03-26 00:00:00 for subject with id 37670>]

# Get timetable
session.get_timetable()
# {'2019-03-18': [<TimetableFrame 08:00->08:45 Historia with Krzysztof ...>, <TimetableFrame 08:55->09:40 Wychowanie fizyczne with Artur ...>, <TimetableFrame 09:50->10:35 Wychowanie fizyczne with Arkadiusz ...>, <TimetableFrame 10:50->11:35 Edukacja dla bezpieczeństwa with Arkadiusz ...>, <TimetableFrame 11:45->12:30 Godzina wychowawcza with Elżbieta ...>, <TimetableFrame 12:50->13:35 Język polski with Aleksandra ...>, <TimetableFrame 13:50->14:35 Język polski with Aleksandra ...>], '2019-03-19': [<TimetableFrame 08:00->08:45 Matematyka with Joanna ...>, <TimetableFrame 08:55->09:40 Matematyka with Joanna ...>, <TimetableFrame 09:50->10:35 Geografia with Agnieszka ...>, <TimetableFrame 10:50->11:35 Wiedza o społeczeństwie with Sylwia ...>, <TimetableFrame 11:45->12:30 Język niemiecki with Elżbieta ...>, <TimetableFrame 12:50->13:35 Matematyka with Joanna ...>], '2019-03-20': [<TimetableFrame 08:00->08:45 Chemia with Edyta ...>, <TimetableFrame 08:55->09:40 Religia with Magdalena ...>, <TimetableFrame 09:50->10:35 Język angielski with Krystyna ...>, <TimetableFrame 10:50->11:35 Etyka with Marta ...>, <TimetableFrame 11:45->12:30 Informatyka with Iwona ...>, <TimetableFrame 12:50->13:35 Język angielski with Krystyna ...>, <TimetableFrame 13:50->14:35 Język niemiecki with Elżbieta ...>], '2019-03-21': [<TimetableFrame 08:00->08:45 Język polski with Aleksandra ...>, <TimetableFrame 08:55->09:40 Język polski with Aleksandra ...>, <TimetableFrame 09:50->10:35 Fizyka with Hieronim ...>, <TimetableFrame 10:50->11:35 Wiedza o kulturze with Elżbieta ...>, <TimetableFrame 11:45->12:30 Religia with Magdalena ...>, <TimetableFrame 12:50->13:35 Język angielski with Krystyna ...>, <TimetableFrame 13:50->14:35 Język angielski with Krystyna ...>], '2019-03-22': [<TimetableFrame 08:00->08:45 Wychowanie fizyczne with Arkadiusz ...>, <TimetableFrame 08:55->09:40 Wychowanie fizyczne with Arkadiusz ...>, <TimetableFrame 09:50->10:35 Informatyka with Iwona ...>, <TimetableFrame 10:50->11:35 Matematyka with Joanna ...>, <TimetableFrame 11:45->12:30 Matematyka with Joanna ...>]}

```

For more examples check the [examples](https://github.com/Backdoorek/Librus-Tricks/tree/prototype/examples) folder

## Screenshots from debugger
![Grade](https://github.com/Backdoorek/public-files/blob/master/pycharm64_2019-03-17_11-29-56.png?raw=true)

## Wrapper in real use
![Example with grades](https://github.com/Backdoorek/public-files/blob/master/2019-03-17_14-32-19.gif?raw=true)
![Example with timetable](https://github.com/Backdoorek/public-files/blob/master/ConEmu64_2019-03-19_18-49-26.png?raw=true)
![Example with attendance](https://github.com/Backdoorek/public-files/blob/master/2019-03-19_19-47-56.gif?raw=true)

Colors in your terminal might be different

> Written with ❤ from a scratch by Krystian _`Backdoorek`_ Postek

> Thanks for guys from [librus-client](https://discord.gg/ybTX4gM) for help with getting into it
