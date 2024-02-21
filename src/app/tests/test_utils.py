from unittest.mock import AsyncMock

import pytest

import app.bot.messages as messages
import settings
from app.db.admins import Admin
from app.db.groups import group_is_added
from app.utils import (
    get_group_id,
    handle_admin_id,
    handle_course,
    handle_faculty,
    make_pairs,
    process_course,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "course, expected",
    [
        ("admin", -1),
        ("0", 0),
        ("1", 1),
        (2, 2),
        ("3", 3),
        ("4", 4),
        ("5", 5),
        ("6", 6),
        ("hello", 0),
    ],
)
async def test_process_course(course, expected):
    assert process_course(course) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "course, expected",
    [
        ("admin", -1),
        ("0", False),
        ("1", 1),
        (2, 2),
        ("3", 3),
        ("4", 4),
        ("5", 5),
        ("6", False),
        ("hello", False),
    ],
)
async def test_handle_course_successful(mocker, course, expected):
    message = mocker.Mock()
    message.answer = mocker.AsyncMock()
    mocker.patch(
        "app.utils.process_course", return_value=process_course(course)
    )
    mock_get_groups_ids = mocker.patch(
        "app.utils.get_groups_ids",
        return_value=[1, 2, 3, 4, 5],
        new_callable=AsyncMock,
    )
    assert await handle_course(message, course, check=True) == expected
    if not expected:
        message.answer.assert_called_once_with("Не верно введен курс!")
    else:
        mock_get_groups_ids.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_course_no_groups(mocker):
    course = "1"

    message = mocker.Mock()
    message.answer = mocker.AsyncMock()
    mocker.patch(
        "app.utils.process_course", return_value=process_course(course)
    )
    mock_get_groups_ids = mocker.patch(
        "app.utils.get_groups_ids", return_value=[], new_callable=AsyncMock
    )
    assert not await handle_course(message, course, check=True)
    message.answer.assert_called_once_with("Произошла непредвиденная ошибка!")
    mock_get_groups_ids.assert_awaited_once()



@pytest.mark.asyncio
@pytest.mark.parametrize(
    "admin_id, need_in_table, from_id, expected",
    [
        # super admin
        ("[id1920129|Администратор_ИКСС]", True, 123, 1920129),
        ("[id1212432122|Администратор_РТС]", True, 123, 1212432122),
        ("[id12345|Already_in_table]", False, 123, False),
        ("1", True, 123, False),
        ("[1212432122|Администратор_ИСИТ]", True, 123, False),
        ("@2012102", True, 123, False),
        ("11298192", True, 123, False),
        ("Name", True, 123, False),
        # not superadmin
        ("[id1920129|Администратор_ИКСС]", True, 321, False),
        ("[id1212432122|Администратор_РТС]", True, 321, False),
        ("[id12345|Already_in_table]", False, 321, False),
        ("1", True, 321, False),
        ("[1212432122|Администратор_ИСИТ]", True, 321, False),
        ("@2012102", True, 321, False),
        ("11298192", True, 321, False),
        ("Name", True, 321, False),
    ],
)
async def test_handle_admin_id_from_superuser(
    mocker, admin_id, need_in_table, from_id, expected
):
    message = mocker.Mock()
    message.from_id = from_id
    message.answer = mocker.AsyncMock()
    all_admins = [
        Admin(id=i, is_superuser=False, faculty_id=f)
        for f, i in enumerate([12345, 54321])
    ]
    mock_get_all_superusers = mocker.patch(
        "app.utils.get_all_superusers",
        return_value=[123],
        new_callable=AsyncMock,
    )
    mock_get_all_admins = mocker.patch(
        "app.utils.get_all_admins",
        return_value=all_admins,
        new_callable=AsyncMock,
    )
    assert await handle_admin_id(message, admin_id, need_in_table) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "text, faculty, expected",
    [
        # super admin
        ("text", "РТС", (1, None, False)),
        ("text123", "суперадмин", (None, None, True)),
        ("text none", "СПБКТ", (None, "text none", None)),
    ],
)
async def test_handle_faculty(mocker, text, faculty, expected):
    message = mocker.Mock()
    message.from_id = 123
    message.answer = mocker.AsyncMock()

    mock_get_faculty_id = mocker.patch(
        "app.utils.get_faculty_id",
        return_value=(messages.faculties.index(faculty) + 1)
        if faculty in messages.faculties
        else None,
        new_callable=AsyncMock,
    )

    assert await handle_faculty(message, text, faculty) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "courses, faculties, expected",
    [
        (
            {1, 2, 3},
            "РТС СПбКТ ИКСС",
            [
                (1, 1),
                (2, 9),
                (3, 2),
                (1, 2),
                (2, 1),
                (3, 9),
                (1, 9),
                (2, 2),
                (3, 1),
            ],
        ),
        ({1, 2, 3}, None, ((1, None), (2, None), (3, None))),
        (
            {-1, 1, 2, 3},
            "ВУЦ ИСиТ",
            [(1, 10), (2, 10), (3, 10), (1, 3), (2, 3), (3, 3)],
        ),
    ],
)
async def test_make_pairs(mocker, courses, faculties, expected):
    async def faculty_id(faculty_name):
        return (
            messages.faculties.index(faculty_name) + 1
            if faculty_name in messages.faculties
            else None
        )

    mock_get_faculty_id = mocker.patch(
        "app.utils.get_faculty_id",
        side_effect=faculty_id,
        new_callable=AsyncMock,
    )
    assert set(await make_pairs(courses, faculties)) == set(expected)


# async def test_proc_course(mocker):
#     pass


# def test_is_valid_id_format(mocker):
#     pass


# def test_extract_id(mocker):
#     pass

# def test_parse_add_regex(mocker):
#     pass


async def test_get_group_id(mocker):
    group_id = 123
    message = mocker.Mock()
    message.peer_id = group_id + settings.GROUP_ID_COEFFICIENT
    assert get_group_id(message) == group_id
