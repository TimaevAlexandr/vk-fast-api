from typing import AsyncGenerator

import pytest
from sqlalchemy.engine import Connection

from app.db import add_group, add_message, connect_message_to_group
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


@pytest.mark.asyncio
@pytest.fixture()
async def groups(init_db):
    await add_group(1, 1)
    await add_group(2, 2)
    await add_group(3, 3)
    yield


@pytest.mark.asyncio
@pytest.fixture()
async def messages(init_db):
    message = await add_message(text="Hello world", attachments=[], author=1)
    await connect_message_to_group(1, message.id, True)
    await connect_message_to_group(2, message.id, True)
    await connect_message_to_group(3, message.id, True)
    yield
