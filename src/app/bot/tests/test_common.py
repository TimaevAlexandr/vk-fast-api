import pytest

from app.bot import messages
from app.bot.common import faculty_list, user_help
from app.db.admins import Admin
from app.vk import bot


@pytest.mark.asyncio
async def test_user_help_successful(mocker):
    message = mocker.AsyncMock()
    message.answer.return_value = 1
    message.from_id = 1

    admins = [
        Admin(id=i, is_superuser=False, faculty_id=f)
        for i, f in zip([1, 2, 3], [1, 2, 3])
    ]
    mocker.patch("app.bot.common.get_all_admins", return_value=admins)

    mocker.patch.object(bot, "api", autospec=True)

    result = await user_help(message)

    assert result == 1
    message.answer.assert_awaited()
    message.answer.assert_called_with(messages.HELP)


@pytest.mark.asyncio
async def test_user_help_not_admin(mocker):
    message = mocker.AsyncMock()
    message.answer.return_value = 1
    message.from_id = 4

    admins = [
        Admin(id=i, is_superuser=False, faculty_id=f)
        for i, f in zip([1, 2, 3], [1, 2, 3])
    ]
    mocker.patch("app.bot.common.get_all_admins", return_value=admins)

    mocker.patch.object(bot, "api", autospec=True)

    result = await user_help(message)

    assert result == 1
    message.answer.assert_awaited()
    message.answer.assert_called_with(messages.FORBIDDEN)


@pytest.mark.asyncio
async def test_faculty_list_super_admin(mocker):
    message = mocker.AsyncMock()
    message.answer.return_value = 1
    message.from_id = 1

    admins = [
        Admin(id=i, is_superuser=True, faculty_id=f)
        for i, f in zip([1, 2, 3], [1, 2, 3])
    ]

    mocker.patch("app.bot.common.get_all_superusers", return_value=admins)

    mocker.patch.object(bot, "api", autospec=True)

    result = await faculty_list(message)

    assert result == 1
    message.answer.assert_awaited()
    message.answer.assert_called_with(messages.FacultiesMessage)


@pytest.mark.asyncio
async def test_faculty_list_not_super_admin(mocker):
    message = mocker.AsyncMock()
    message.answer.return_value = 1
    message.from_id = 4

    admins = [
        Admin(id=i, is_superuser=True, faculty_id=f)
        for i, f in zip([1, 2, 3], [1, 2, 3])
    ]
    mocker.patch("app.bot.common.get_all_superusers", return_value=admins)

    mocker.patch.object(bot, "api", autospec=True)

    result = await faculty_list(message)

    assert result == 1
    message.answer.assert_awaited()
    message.answer.assert_called_with(messages.FORBIDDEN)
