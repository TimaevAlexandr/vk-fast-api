import pytest
from sqlalchemy import select
from sqlalchemy.engine import Connection
from sqlalchemy.exc import DBAPIError

from app.db import (
    Base,
    StudentGroup,
    add_group,
    change_group_course,
    db_connect,
    delete_group,
    engine,
    groups_ids,
    ids_by_course,
)
from app.exceptions import DBError


@pytest.fixture()
def connection() -> Connection:
    conn = engine.connect()
    yield conn
    conn.close()


@pytest.fixture()
def init_db(connection: Connection):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_add_group(init_db):
    group_id = 1
    course = 2021
    add_group(group_id, course)
    with engine.connect() as conn:
        result = conn.execute(
            select(StudentGroup).where(StudentGroup.id == group_id)
        ).first()
    assert result.id == group_id
    assert result.course == course


def test_ids_by_course(init_db):
    group_id = 2
    course = 2022
    add_group(group_id, course)
    assert [group_id] == ids_by_course(course)


def test_delete_group(init_db):
    group_id = 3
    course = 2023
    add_group(group_id, course)
    delete_group(group_id)
    with engine.connect() as conn:
        result = conn.execute(
            select(StudentGroup).where(StudentGroup.id == group_id)
        ).first()
    assert result is None


def test_groups_ids(init_db):
    group_ids_to_add = [4, 5, 6]
    for gid in group_ids_to_add:
        add_group(gid, 2024)
    assert set(group_ids_to_add) == set(groups_ids())


def test_change_group_course(init_db):
    group_id = 7
    course = 2025
    add_group(group_id, course)
    new_course = 2026
    change_group_course(group_id, new_course)
    with engine.connect() as conn:
        result = conn.execute(
            select(StudentGroup).where(StudentGroup.id == group_id)
        ).first()
    assert result.course == new_course


def test_db_connect_raises_database_error(mocker, init_db):
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
        decorated_func()

    log_mock.assert_called_with("Database error")


def test_db_connect_raises_unexpected_error(mocker, init_db):
    log_critical_mock = mocker.patch("logging.critical")

    mocked_func = mocker.Mock(side_effect=Exception("Unexpected Error"))
    decorated_func = db_connect(mocked_func)

    with pytest.raises(DBError):
        decorated_func()

    # Assert the expected logging call
    log_critical_mock.assert_called_with("Unexpected error")
