# LibrusTricks
A powerful python Librus Synergia API based on RE

## Install
```text
pip install git+https://github.com/Backdoorek/LibrusTricks.git@prototype
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

> Written with ❤ from a scratch by Krystian _`Backdoorek`_ Postek

> Thanks for guys from [librus-client](https://discord.gg/ybTX4gM) for help with getting into it