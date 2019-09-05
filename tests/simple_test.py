import asyncio
import os
import sys

sys.path.extend(['./'])

email = os.environ['librus_email']
password = os.environ['librus_password']

from librus_tricks import create_session

loop = asyncio.get_event_loop()

# def test_auth():
#     async def wrapped():
#         session = await create_session(email, password)
#         return await session.user.is_revalidation_required(use_query=True)
# 
#     loop.run_until_complete(wrapped())


def test_grades():
    async def wrapped():
        session = await create_session(email, password)
        return await session.return_grades()

    loop.run_until_complete(wrapped())
