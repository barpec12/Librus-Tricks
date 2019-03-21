# LibrusTricks
[![Build Status](https://travis-ci.org/Backdoorek/LibrusTricks.svg?branch=prototype)](https://travis-ci.org/Backdoorek/LibrusTricks)

A powerful python Librus Synergia API based on RE

## Install
```text
# Windows
# Latest stable alpha
pip install git+https://github.com/Backdoorek/LibrusTricks.git@proto-0.1.0

# Latest alpha
pip install git+https://github.com/Backdoorek/LibrusTricks.git@prototype

# Linux
# Latest stable alpha
sudo -H pip3 install git+https://github.com/Backdoorek/LibrusTricks.git@proto-0.1.0

# Latest alpha
sudo -H pip3 install git+https://github.com/Backdoorek/LibrusTricks.git@prototype
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

```

For more examples check the [examples](https://github.com/Backdoorek/LibrusTricks/tree/prototype/examples) folder

## Screenshots from debugger
![Grade](https://github.com/Backdoorek/public-files/blob/master/pycharm64_2019-03-17_11-29-56.png?raw=true)

## Wrapper in real use
![Example with grades](https://github.com/Backdoorek/public-files/blob/master/2019-03-17_14-32-19.gif?raw=true)
![Example with timetable](https://github.com/Backdoorek/public-files/blob/master/ConEmu64_2019-03-19_18-49-26.png?raw=true)
![Example with attendance](https://github.com/Backdoorek/public-files/blob/master/2019-03-19_19-47-56.gif?raw=true)

Colors in your terminal might be different

> Written with ❤ from a scratch by Krystian _`Backdoorek`_ Postek

> Thanks for guys from [librus-client](https://discord.gg/ybTX4gM) for help with getting into it
