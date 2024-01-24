import pytest
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError

from app.db.common import db_connect, engine
from app.db.groups import (
    StudentGroup,
    add_group,
    change_group_course,
    delete_group,
    get_group_ids_by_course,
    get_groups_ids,
)
from app.db.messages import (  # with - 5 not passed. without - 13 not passed
    Message,
)
from app.exceptions import DBError


@pytest.mark.asyncio
async def test_add_group(init_db):
    group_id = 1
    course = 2021
    faculty_id = 1
    await add_group(group_id, course, faculty_id)
    async with engine.connect() as conn:
        result = (
            await conn.execute(
                select(StudentGroup).where(StudentGroup.id == group_id)
            )
        ).first()
    assert result.id == group_id
    assert result.course == course
    assert result.faculty_id == faculty_id


@pytest.mark.asyncio
async def test_ids_by_course(init_db):
    group_id = 2
    course = 2022
    faculty_id = 2
    await add_group(group_id, course, faculty_id)
    assert [group_id] == await get_group_ids_by_course(course)


@pytest.mark.asyncio
async def test_delete_group(init_db):
    group_id = 3
    course = 2023
    faculty_id = 33
    await add_group(group_id, course, faculty_id)
    await delete_group(group_id)
    async with engine.connect() as conn:
        result = (
            await conn.execute(
                select(StudentGroup).where(StudentGroup.id == group_id)
            )
        ).first()
    assert result is None


@pytest.mark.asyncio
async def test_groups_ids(init_db):
    await add_group(4, 2024, 44)
    await add_group(5, 2024, 55)
    await add_group(6, 2024, 66)

    groups_ids = await get_groups_ids()

    assert set([4, 5, 6]) == set(groups_ids)


@pytest.mark.asyncio
async def test_change_group_course(init_db):
    group_id = 7
    course = 2025
    faculty_id = 77

    await add_group(group_id, course, faculty_id)

    new_course = 2026

    await change_group_course(group_id, new_course)
    async with engine.connect() as conn:
        result = (
            await conn.execute(
                select(StudentGroup).where(StudentGroup.id == group_id)
            )
        ).first()
    assert result.course == new_course


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
