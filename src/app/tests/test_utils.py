from unittest.mock import AsyncMock

import pytest

import settings
from app.utils import handle_course, handle_group, process_course #, handle_admin


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
        ("admin", True),
        ("0", False),
        ("1", True),
        (2, True),
        ("3", True),
        ("4", True),
        ("5", True),
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
    "group_id, groups_ids, expected",
    [
        (1, [1, 2, 3], (None, "text")),
        (2, [1, 2, 3], (None, "text")),
        (3, [1, 2, 3], (None, "text")),
        (4, [1, 2, 3], (4, None)),
    ],
)
async def test_handle_group_successful(mocker, group_id, groups_ids, expected):
    message = mocker.Mock()
    message.peer_id = group_id + settings.GROUP_ID_COEFFICIENT
    message.answer = mocker.AsyncMock()
    mock_get_groups_ids = mocker.patch(
        "app.utils.get_groups_ids",
        return_value=groups_ids,
        new_callable=AsyncMock,
    )
    assert await handle_group(message, "text") == expected
    if not expected[0]:
        message.answer.assert_called_once_with("text")
    else:
        mock_get_groups_ids.assert_awaited_once()

async def test_handle_admin():
    pass