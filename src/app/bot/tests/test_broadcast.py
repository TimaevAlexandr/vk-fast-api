import pytest
from pytest_lazy_fixtures import lf
from vkbottle.user import Message

from app.bot.broadcast import sharing_text
from app.db.admins import Admin

@pytest.fixture()
def attachment(mocker):
    attach = mocker.Mock()
    attach.owner_id = 1
    attach.id = 1
    return attach


@pytest.fixture()
def message_simple(mocker, attachment):
    msg = mocker.Mock()
    msg.answer = mocker.AsyncMock(return_value=1)
    msg.from_id = 1
    msg.get_wall_attachment.return_value = [attachment]
    msg.fwd_messages = []
    msg.reply_message = None
    msg.text = "рассылка: 123 text"
    return msg


@pytest.fixture()
def message_with_reply(mocker, message_simple):
    reply = mocker.Mock()
    reply.text = "text"
    message_simple.reply_message = reply
    return message_simple


@pytest.fixture()
def message_with_fwd(mocker, message_simple):
    reply = mocker.Mock()
    reply.text = "text"
    message_simple.fwd_messages = [reply]
    return message_simple


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "message",
    (
        lf("message_simple"),
        lf("message_with_reply"),
        lf("message_with_fwd"),
    ),
)
@pytest.mark.parametrize(
    "broadcast_result, expected_result",
       [
        (
            (
                (
                    1,
                    (True,),
                    "РТС",
                ),
                (
                    2,
                    (True,),
                    "РТС",
                ),
                (
                    3,
                    (True,),
                    "РТС",
                ),
            ),
            "Рассылка успешно отправлена!\n\n"
            "Курс 1 факультет РТС: +\n"
            "Курс 2 факультет РТС: +\n"
            "Курс 3 факультет РТС: +",
        ),
        (
            (
                (
                    1,
                    (False,),
                    "ИКСС",
                ),
                (
                    2,
                    (False,),
                    "ИКСС",
                ),
                (
                    3,
                    (False,),
                    "ИКСС",
                ),
            ),
            "Не удалось отправить рассылку.\n\n"
            "Курс 1 факультет ИКСС: -\n"
            "Курс 2 факультет ИКСС: -\n"
            "Курс 3 факультет ИКСС: -",
        ),
        (
            (
                (
                    1,
                    (False,),
                    "ИСиТ",
                    
                ),
                (
                    2,
                    (True,),
                    "ИСиТ",
                ),
                (
                    3,
                    (True,),
                    "ИСиТ",
                ),
            ),
            "Рассылка отправлена не полностью.\n\n"
            "Курс 1 факультет ИСиТ: -\n"
            "Курс 2 факультет ИСиТ: +\n"
            "Курс 3 факультет ИСиТ: +",
        ),
    ],
)
async def test_sharing_text(
    message: Message,
    broadcast_result: tuple[tuple[int, tuple[bool]]],
    expected_result: str,
    mocker,
):

    admins = [
        Admin(id=i, is_superuser=False, faculty_id=f) for i, f in zip([1, 2, 3], [1, 2, 3])
    ]
    mocker.patch("app.bot.broadcast.get_all_admins", return_value=admins)

    broadcast_mock = mocker.patch(
        "app.bot.broadcast.broadcast",
        new_callable=mocker.AsyncMock,
        return_value=broadcast_result,
    )

    parse_text_mock =  mocker.patch("app.bot.broadcast.parse_text", return_value=("123", None, "text"))
    mocker.patch("app.bot.broadcast.get_text", return_value="text")
    mocker.patch("app.bot.broadcast.get_attachments", return_value="wall1_1")

    # message.answer = mocker.AsyncMock()

    await sharing_text(message)

    message.answer.assert_called_with(expected_result)

    broadcast_mock.assert_called_with(
        "123", None , message.from_id , text="text", attachment=["wall1_1"]
    )

    parse_text_mock.assert_called_with(message)
    message.answer.assert_awaited()
    broadcast_mock.assert_awaited()


@pytest.mark.asyncio
async def test_sharing_text_forbidden(mocker):
    message = mocker.Mock()
    message.from_id = 4

    admins = [
        Admin(id=i, is_superuser=False, faculty_id=f) for i, f in zip([1, 2, 3], [1, 2, 3])
    ]
    mocker.patch("app.bot.broadcast.get_all_admins", return_value=admins)
    broadcast_mock = mocker.patch("app.bot.broadcast.broadcast")
    message.text = "рассылка: 1. text"

    await sharing_text(message)
    message.answer.asser_awaited()
    broadcast_mock.assert_not_called() # админ не проходит