from typing import AsyncGenerator

import pytest
from sqlalchemy.engine import Connection

from app.db.common import Base, engine


@pytest.mark.asyncio
@pytest.fixture()
async def connection() -> AsyncGenerator[Connection, None]:
    conn = await engine.connect()
    yield conn
    await conn.close()


@pytest.mark.asyncio
@pytest.fixture()
async def init_db(connection: Connection):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# @pytest.mark.asyncio
# @pytest.fixture()
# async def faculties(init_db):
#     await add_faculty(1, "ИКСС")
#     await add_faculty(2, "ИСИТ")
#     await add_faculty(3, "ВУЦ")
#     await add_faculty(4, "ЦЭУБИ")
#     yield


# @pytest.mark.asyncio
# @pytest.fixture()
# async def groups(init_db):
#     await add_group(1, 1, 1)
#     await add_group(2, 2, 2)
#     await add_group(3, 3, 3)
#     yield


# @pytest.mark.asyncio
# @pytest.fixture()
# async def admins(init_db):
#     await add_admin(False, 1)
#     await add_admin(False, 2)
#     await add_admin(False, 3)
#     yield
