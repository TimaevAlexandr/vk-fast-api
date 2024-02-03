import pytest
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError

from app.db.common import db_connect, engine
from app.db.groups import (
    StudentGroup,
    GroupMessage,
    add_group,
    change_group_course,
    delete_group,
    get_course_by_group_id,
    get_group_ids_by_course,
    get_groups_ids,
    connect_message_to_group,
)
from app.db.messages import add_message, Message
from app.exceptions import DBError


@pytest.mark.asyncio
async def test_add_group(init_db):
    group_id = 1
    course = 2021
    await add_group(group_id, course)
    async with engine.connect() as conn:
        result_message = (
            await conn.execute(
                select(StudentGroup).where(StudentGroup.id == group_id)
            )
        ).first()
    assert result_message.id == group_id
    assert result_message.course == course


@pytest.mark.asyncio
async def test_ids_by_course(init_db):
    group_id = 2
    course = 2022
    await add_group(group_id, course)
    assert [group_id] == await get_group_ids_by_course(course)


@pytest.mark.asyncio
async def test_get_course_by_group_id(init_db):
    group_id = 2
    course = 2022
    await add_group(group_id, course)
    assert course == await get_course_by_group_id(group_id)
    assert await get_course_by_group_id(3456) is None


@pytest.mark.asyncio
async def test_delete_group(init_db):
    group_id = 3
    course = 2023
    await add_group(group_id, course)
    await delete_group(group_id)
    async with engine.connect() as conn:
        result_message = (
            await conn.execute(
                select(StudentGroup).where(StudentGroup.id == group_id)
            )
        ).first()
    assert result_message is None


@pytest.mark.asyncio
async def test_groups_ids(init_db):
    group_ids_to_add = [4, 5, 6]
    for gid in group_ids_to_add:
        await add_group(gid, 2024)
    assert set(group_ids_to_add) == set(await get_groups_ids())


@pytest.mark.asyncio
async def test_change_group_course(init_db):
    group_id = 7
    course = 2025
    await add_group(group_id, course)
    new_course = 2026
    await change_group_course(group_id, new_course)
    async with engine.connect() as conn:
        result_message = (
            await conn.execute(
                select(StudentGroup).where(StudentGroup.id == group_id)
            )
        ).first()
    assert result_message.course == new_course


@pytest.mark.asyncio
async def test_db_connect_raises_database_error(mocker, init_db):
    log_mock = mocker.patch("logging.error")

    mocked_func = mocker.Mock(
        side_effect=DBAPIError(
            "DB Error",
            None,
            None,
        )
    )
    decorated_func = db_connect(mocked_func)

    with pytest.raises(DBError):
        await decorated_func()

    log_mock.assert_called_with("Database error")


@pytest.mark.asyncio
async def test_db_connect_raises_unexpected_error(mocker, init_db):
    log_critical_mock = mocker.patch("logging.critical")

    mocked_func = mocker.Mock(side_effect=Exception("Unexpected Error"))
    decorated_func = db_connect(mocked_func)

    with pytest.raises(DBError):
        await decorated_func()

    # Assert the expected logging call
    log_critical_mock.assert_called_with("Unexpected error")


@pytest.mark.asyncio
async def test_add_message(init_db):
    group_id = 1
    course = 1
    await add_group(group_id, course)
    message_id = 1
    text = "hello world"
    attachment = []
    author = 1
    date = datetime.now()
    recieved = True
    message: Message = await add_message(text, attachment, author, date)
    await connect_message_to_group(group_id, message, recieved)
    async with engine.connect() as conn:
        result_message = (
            await conn.execute(
                select(Message).where(Message.id == message_id)
            )
        ).first()
        result_association = (
            await conn.execute(
                select(GroupMessage).where(GroupMessage.student_groups_id == group_id)
            )
        ).first()
    assert result_message.text == text
    assert result_message.attachment == attachment
    assert result_message.date == date
    assert result_message.author == author
    assert result_association.messages_id == message_id
    assert result_association.received == recieved
