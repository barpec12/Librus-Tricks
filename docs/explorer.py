import asyncio
import json
import os
import sys

from librus_tricks import create_session

email, password = sys.argv[1:3]


async def save_api(*path):
    session = await create_session(email, password)
    uri = session.assembly_path(*path, prefix='https://api.librus.pl/2.0/')
    response = await session.httpx.get(uri, headers={'Authorization': f'Bearer {session.user.token}'})
    status = response.status_code
    file_path = session.assembly_path(*path, suffix=f'/{status}.json')
    response = response.json()

    if not os.path.exists(file_path.replace(f'{status}.json', '')):
        os.makedirs(file_path.replace(f'{status}.json', ''))

    with open(file_path, mode='w', encoding='utf-8') as output:
        print(json.dumps(response, indent=2, ensure_ascii=False))
        json.dump(response, output, indent=2, ensure_ascii=False)
        output.close()


if __name__ == '__main__':
    asyncio.run(save_api(sys.argv[3]))
