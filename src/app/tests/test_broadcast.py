from unittest.mock import AsyncMock, call

import pytest
from vkbottle import VKAPIError
from vkbottle.exception_factory.code_exception import CodeExceptionMeta

import settings
from app.broadcast import (
    all_groups_broadcast,
    broadcast,
    course_broadcast,
    group_broadcast,
)
from app.db.admins import Admin
from app.db.messages import Message
from app.exceptions import DBError
from app.vk import bot


class VKAPIErrorPermissionDenied(  # type: ignore[call-arg]
    VKAPIError,
    code=7,
    metaclass=CodeExceptionMeta,
):
    ...


class VKAPICommonError(  # type: ignore[call-arg]
    VKAPIError,
    code=1,
    metaclass=CodeExceptionMeta,
):
    ...


@pytest.mark.asyncio
async def test_group_broadcast_successful(mocker):
    group = 1
    text = "hello world!"
    attachment = ["123"]

    mocker.patch.object(bot, "api", autospec=True)

    bot.api.messages.send = AsyncMock()
    bot.api.messages.send.return_value = 1

    result = await group_broadcast(group, text, attachment)
    assert result == 1
    bot.api.messages.send.assert_awaited()
    bot.api.messages.send.assert_called_with(
        peer_id=(settings.GROUP_ID_COEFFICIENT + group),
        message=text,
        attachment=attachment,
        random_id=0,
    )


@pytest.mark.asyncio
async def test_group_broadcast_permissions_failed(mocker):
    log_mock = mocker.patch("app.broadcast.logger.warning")

    group = 1
    text = "hello world!"
    attachment = ["123"]

    mocker.patch.object(bot, "api", autospec=True)

    error = VKAPIErrorPermissionDenied(
        error_msg="Permission to perform this action is denied by user"
    )
    bot.api.messages.send = AsyncMock(side_effect=error)

    delete_group_mock = mocker.patch(
        "app.broadcast.delete_group", new_callable=AsyncMock
    )

    result = await group_broadcast(group, text, attachment)

    assert not result
    bot.api.messages.send.assert_awaited()
    delete_group_mock.assert_awaited()
    delete_group_mock.assert_called_once_with(group)
    log_mock.assert_called_with(error)


@pytest.mark.asyncio
async def test_group_broadcast_failed(mocker):
    log_mock = mocker.patch("app.broadcast.logger.error")

    group = 1
    text = "hello world!"
    attachment = ["123"]

    mocker.patch.object(bot, "api", autospec=True)

    error = VKAPICommonError(error_msg="Error")
    bot.api.messages.send = AsyncMock(side_effect=error)

    result = await group_broadcast(group, text, attachment)

    assert not result
    bot.api.messages.send.assert_awaited()
    log_mock.assert_called_with(error)


@pytest.mark.asyncio
async def test_all_groups_broadcast_successful(mocker):
    from_id = 1
    text = "hello world!"
    attachment = ["123"]
    groups_ids = [1, 2, 3]

    mocker.patch.object(bot, "api", autospec=True)

    bot.api.messages.send = AsyncMock()
    bot.api.messages.send.return_value = 1

    get_groups_ids_mock = mocker.patch(
        "app.broadcast.get_groups_ids",
        new_callable=AsyncMock,
    )
    get_groups_ids_mock.return_value = groups_ids

    connect_message_to_group_mock = mocker.patch(
        "app.broadcast.connect_message_to_group",
        new_callable=AsyncMock,
    )
    connect_message_to_group_mock.return_value = None

    result = await all_groups_broadcast(from_id, text, attachment)

    assert result == ("ВСЕ", tuple([True, True, True]), "ВСЕ")
    bot.api.messages.send.assert_awaited()

    expected_calls = [
        call(
            peer_id=(settings.GROUP_ID_COEFFICIENT + group),
            message=text,
            attachment=attachment,
            random_id=0,
        )
        for group in groups_ids
    ]
    bot.api.messages.send.assert_has_calls(expected_calls, any_order=True)


@pytest.mark.asyncio
async def test_all_groups_broadcast_permission_failed(mocker):
    log_mock = mocker.patch("app.broadcast.logger.warning")
    text = "hello world!"
    attachment = ["123"]
    groups_ids = [1, 2, 3]
    from_id = 1

    mocker.patch.object(bot, "api", autospec=True)

    error = VKAPIErrorPermissionDenied(
        error_msg="Permission to perform this action is denied by user"
    )
    bot.api.messages.send = AsyncMock(side_effect=error)

    get_groups_ids_mock = mocker.patch(
        "app.broadcast.get_groups_ids",
        new_callable=AsyncMock,
    )
    get_groups_ids_mock.return_value = groups_ids

    connect_message_to_group_mock = mocker.patch(
        "app.broadcast.connect_message_to_group",
        new_callable=AsyncMock,
    )
    connect_message_to_group_mock.return_value = None

    delete_group_mock = mocker.patch(
        "app.broadcast.delete_group", new_callable=AsyncMock
    )
    delete_group_mock.return_value = None

    result = await all_groups_broadcast(from_id, text, attachment)

    assert result == ("ВСЕ", (False, False, False), "ВСЕ")
    bot.api.messages.send.assert_awaited()
    get_groups_ids_mock.assert_awaited()
    get_groups_ids_mock.assert_called_once()
    log_mock.assert_called_with(error)


@pytest.mark.asyncio
async def test_all_groups_broadcast_failed(mocker):
    log_mock = mocker.patch("app.broadcast.logger.error")
    text = "hello world!"
    attachment = ["123"]
    from_id = 1

    mocker.patch.object(bot, "api", autospec=True)

    error = DBError("Error")

    get_groups_ids_mock = mocker.patch(
        "app.broadcast.get_groups_ids",
        new_callable=AsyncMock,
    )
    add_message_mock = mocker.patch(
        "app.broadcast.add_message", new_callable=AsyncMock
    )
    add_message_mock.return_value = Message(
        text=text, attachments=attachment, author=from_id
    )

    get_groups_ids_mock.side_effect = error

    result = await all_groups_broadcast(from_id, text, attachment)

    assert result == ("не найден", (False,), "не найден")
    log_mock.assert_called_with(error)
    pass


@pytest.mark.asyncio
async def test_course_broadcast_empty(mocker):
    course = 2023
    text = "hello world!"
    attachment = ["123"]
    from_id = 1
    faculty_id = 1

    mocker.patch.object(bot, "api", autospec=True)

    get_group_ids_by_course_faculty_id_mock = mocker.patch(
        "app.broadcast.get_group_ids_by_course_faculty_id",
        new_callable=AsyncMock,
    )
    get_group_ids_by_course_faculty_id_mock.return_value = []
    get_faculty_name_mock = mocker.patch(
        "app.broadcast.get_faculty_name", new_callable=AsyncMock
    )

    get_faculty_name_mock.return_value = "РТС"
    result = await course_broadcast(
        course, from_id, text, attachment, faculty_id
    )

    assert result == (course, (False,), "РТС")
    get_group_ids_by_course_faculty_id_mock.assert_awaited()
    get_group_ids_by_course_faculty_id_mock.assert_called_once_with(
        course, faculty_id
    )


@pytest.mark.asyncio
async def test_course_broadcast_exception(mocker):
    log_mock = mocker.patch("app.broadcast.logger.error")

    course = 2023
    text = "hello world!"
    attachment = ["123"]
    from_id = 1
    faculty_id = 1

    mocker.patch.object(bot, "api", autospec=True)

    error = DBError("Error")

    get_group_ids_by_course_faculty_id_mock = mocker.patch(
        "app.broadcast.get_group_ids_by_course_faculty_id",
        new_callable=AsyncMock,
    )

    add_message_mock = mocker.patch(
        "app.broadcast.add_message", new_callable=AsyncMock
    )
    add_message_mock.return_value = Message(
        text=text, attachments=attachment, author=from_id
    )

    get_group_ids_by_course_faculty_id_mock.side_effect = error
    get_faculty_name_mock = mocker.patch(
        "app.broadcast.get_faculty_name", new_callable=AsyncMock
    )

    get_faculty_name_mock.return_value = "РТС"

    result = await course_broadcast(
        course, add_message_mock.return_value, text, attachment, faculty_id
    )

    assert result == (course, (False,), "РТС")
    log_mock.assert_called_with(error)


@pytest.mark.asyncio
async def test_course_broadcast_successful(mocker):
    course = 2023
    text = "hello world!"
    attachment = ["123"]
    from_id = 1
    faculty_id = 1

    mocker.patch.object(bot, "api", autospec=True)

    get_group_ids_by_course_faculty_id_mock = mocker.patch(
        "app.broadcast.get_group_ids_by_course_faculty_id",
        new_callable=AsyncMock,
    )
    get_group_ids_by_course_faculty_id_mock.return_value = [1, 2, 3]

    group_broadcast_mock = mocker.patch(
        "app.broadcast.group_broadcast", new_callable=AsyncMock
    )
    group_broadcast_mock.return_value = True

    get_faculty_name_mock = mocker.patch(
        "app.broadcast.get_faculty_name", new_callable=AsyncMock
    )

    add_message_mock = mocker.patch(
        "app.broadcast.add_message", new_callable=AsyncMock
    )
    add_message_mock.return_value = Message(
        text=text, attachments=attachment, author=from_id
    )

    get_faculty_name_mock.return_value = "РТС"

    connect_message_to_group_mock = mocker.patch(
        "app.broadcast.connect_message_to_group", new_callable=AsyncMock
    )
    connect_message_to_group_mock.return_value = None

    result = await course_broadcast(
        course, add_message_mock.return_value, text, attachment, faculty_id
    )

    assert result == (course, (True,) * 3, "РТС")
    get_group_ids_by_course_faculty_id_mock.assert_awaited()
    get_group_ids_by_course_faculty_id_mock.assert_called_once_with(
        course, faculty_id
    )
    group_broadcast_mock.assert_awaited()
    group_broadcast_mock.assert_has_awaits(
        [
            mocker.call(
                1,
                text,
                attachment,
            ),
            mocker.call(
                2,
                text,
                attachment,
            ),
            mocker.call(
                3,
                text,
                attachment,
            ),
        ]
    )


@pytest.mark.asyncio
async def test_broadcast_empty(mocker):
    courses = "2023"
    text = "hello world!"
    attachment = ["123"]
    from_id = 1
    faculty_id = 1
    faculties = None  # as it is not superadmin

    mocker.patch.object(bot, "api", autospec=True)
    admin = Admin(id=from_id, is_superuser=False, faculty_id=faculty_id)

    mocker.patch("app.broadcast.get_admin_by_id", return_value=admin)

    course_broadcast_mock = mocker.patch(
        "app.broadcast.course_broadcast", new_callable=AsyncMock
    )
    course_broadcast_mock.return_value = (False,)

    add_message_mock = mocker.patch(
        "app.broadcast.add_message", new_callable=AsyncMock
    )
    add_message_mock.return_value = Message(
        text=text, attachments=attachment, author=from_id
    )

    connect_message_to_group_mock = mocker.patch(
        "app.broadcast.connect_message_to_group", new_callable=AsyncMock
    )
    connect_message_to_group_mock.return_value = None
    result = await broadcast(courses, faculties, from_id, text, attachment)
    assert (
        result == ((False,),) * 2
    )  # broadcast.proc_course remove 0 from courses
    course_broadcast_mock.assert_awaited()
    course_broadcast_mock.assert_has_awaits(
        [
            mocker.call(
                2,from_id , text, attachment, faculty_id
            ),
            mocker.call(
                3, from_id, text, attachment, faculty_id
            ),
        ]
    )


@pytest.mark.asyncio
async def test_broadcast_successful(mocker):
    courses = "2023"
    text = "hello world!"
    attachment = ["123"]
    from_id = 1
    faculty_id = 1
    faculties = None  # as it is not superadmin

    mocker.patch.object(bot, "api", autospec=True)

    admin = Admin(id=from_id, is_superuser=False, faculty_id=faculty_id)

    mocker.patch("app.broadcast.get_admin_by_id", return_value=admin)
    course_broadcast_mock = mocker.patch(
        "app.broadcast.course_broadcast", new_callable=AsyncMock
    )
    course_broadcast_mock.return_value = (True,)
    add_message_mock = mocker.patch(
        "app.broadcast.add_message", new_callable=AsyncMock
    )
    add_message_mock.return_value = Message(
        text=text, attachments=attachment, author=from_id
    )

    connect_message_to_group_mock = mocker.patch(
        "app.broadcast.connect_message_to_group", new_callable=AsyncMock
    )
    connect_message_to_group_mock.return_value = None
    result = await broadcast(courses, faculties, from_id, text, attachment)

    assert result == ((True,),) * 2
    course_broadcast_mock.assert_awaited()
    course_broadcast_mock.assert_has_awaits(
        [
            mocker.call(
                2, from_id, text, attachment, faculty_id
            ),
            mocker.call(
                3, from_id, text, attachment, faculty_id
            ),
        ]
    )


@pytest.mark.asyncio
async def test_broadcast_not_numeric_error(mocker):
    courses = "qwe"
    text = "hello world!"
    attachment = ["123"]
    from_id = 1
    faculties = None
    faculty_id = 1

    log_mock = mocker.patch("app.broadcast.logger.error")

    admin = Admin(id=from_id, is_superuser=False, faculty_id=faculty_id)

    mocker.patch("app.broadcast.get_admin_by_id", return_value=admin)

    result = await broadcast(courses, faculties, from_id, text, attachment)

    assert not result

    log_mock.assert_called_with("Courses is not valid")
