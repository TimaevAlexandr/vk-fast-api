import logging

from fastapi import APIRouter, Request, Response
from vkbottle import VKAPIError
from vkbottle.bot import Bot, Message

import settings
from app.db import add_group, delete_group, groups_ids, ids_by_course

app = APIRouter(prefix="/api", tags=["API"])

bot = Bot(settings.VK_TOKEN)

bot.labeler.vbml_ignore_case = True


async def broadcast(
    courses: str, text: str | None = None, attachment: list | None = None
) -> None:
    for course in courses:
        for group in ids_by_course(int(course)):
            try:
                await bot.api.messages.send(
                    peer_id=(settings.GROUP_ID_COEFFICIENT + group),
                    message=text,
                    attachment=attachment,
                    random_id=0,
                )
            except VKAPIError[7] as exception:
                logging.warning(exception)
                delete_group(group)
            except VKAPIError as exception:
                logging.error(exception)

async def process_course(course: str | int) -> int:
    if course == "admin":
        return -1
    if isinstance(course, str) and course.isnumeric():
        return int(course)
    return 0

@bot.on.chat_message(text="Рассылка: <courses>, Текст <text>")
async def sharing_text(message: Message, courses: str, text: str) -> None:
    if message.from_id not in settings.ADMINS:
        return
    await broadcast(courses, text=text)


@bot.on.chat_message(text="Рассылка: <courses>, Пост")
async def share_publication(message: Message, courses: str) -> None:
    if message.from_id not in settings.ADMINS:
        return
    attachment = message.get_wall_attachment()
    if len(attachment) != 0:
        attachment = attachment[0]
        await broadcast(
            courses, attachment=[f"wall{attachment.owner_id}_{attachment.id}"]
        )
    else:
        message.forward("Ошибка пост не был прикреплен!")


@bot.on.chat_message(text="Рассылка: <courses>, Сообщение")
async def share_message(message: Message, courses: str) -> None:
    if message.from_id not in settings.ADMINS:
        return

    if message.fwd_messages:
        await broadcast(courses, text=message.fwd_messages[0].text)
    else:
        await message.answer("Ошибка: нет пересланного сообщения")


@bot.on.chat_message(text="Изменить <course>")
async def change_course(message: Message, course: str | int) -> None:
    if (course := process_course(course)) == 0:
        await message.answer("Не верно введен курс!")
        return

@bot.on.chat_message(text="Добавить <course>")
async def add(message: Message, course: str | int) -> None:
    if (course := process_course(course)) == 0:
        await message.answer("Не верно введен курс!")
        return

    if int(course) not in (-1, 1, 2, 3, 4, 5):
        await message.answer("Не верно введен курс!")
        return

    group_id = message.peer_id - settings.GROUP_ID_COEFFICIENT

    if group_id in groups_ids():
        await message.answer("Ваша беседа уже есть в списке")
        return

    add_group(group_id, course)

    await message.answer("Ваша беседа успешно добавлена!")
    await message.answer(
        "Добро пожаловать в беседу!\n\n"
        "Этот чат создан специально для "
        f"студентов {course} курса факультета ИКСС. "
        "Здесь будет собрана только важная информация, "
        "которую вы обязаны знать!\n\n"
        "В данном чате есть правила, ниже вы можете с ними ознакомиться.\n"
        "🟧Писать здесь могут только:\n"
        "👉🏼 Староста\n"
        "👉🏼 Зам. старосты\n"
        "👉🏼 Бот\n"
        "Для остальных участников данный чат доступен "
        "только для просмотра информации.\n"
        "🟧Запрещено писать сообщения без предварительного "
        "согласования их со старостой или его заместителем.\n\n"
        "🟧 Полезные ресурсы:\n"
        "✅Бот в Телеграм: https://t.me/BonchGUTBot\n"
        "✅Сайт Бонча: https://www.sut.ru\n"
        "✅ГУТ.Навигатор: https://nav.sut.ru/?cab=k2-117\n"
        "✅Студгородок: https://vk.com/campusut\n"
        "✅Факультет ИКСС: https://vk.com/iksssut\n"
        "✅Группа СПбГУТ: https://vk.com/sutru\n"
        "✅Студсовет: https://vk.com/studsovet.bonch\n"
        "✅InGUT: https://vk.com/ingut\n"
        "✅Подслушано Бонч: https://vk.com/overhear_bonch\n"
        "✅Bonch Media: https://vk.com/bonch.media\n"
        "✅Memgut: https://vk.com/bonchmemes\n"
        "✅Гутка: https://vk.com/gutka_sut\n"
        "✅Первокурсники СПбГУТ: https://vk.com/onegut\n\n"
        "По вопросам и предложениям писать @pavel.cmake(разработчику)"
    )


@bot.on.chat_message(text="Помощь")
async def user_help(message: Message) -> None:
    if message.from_id in settings.ADMINS:
        await message.answer(
            "Команды:\n\n"
            "Добавить <course> - Добавляет беседу в БД, "
            "флаг admin значит что в беседу не будут приходить новости\n\n"
            "Рассылка: <courses>, Сообщение - "
            "Рассылает пересланное сообщение\n\n"
            "Рассылка: <courses>, Пост - Рассылает пересланный пост\n\n"
            "Рассылка: <courses>, Текст <text> - Рассылает набранный текст"
        )


@app.post("/callback")
async def callback(request: Request) -> Response:
    data = await request.json()
    if data.get("type") == "confirmation" and data.get("group_id") == int(
        settings.GROUP_ID
    ):
        return Response(
            media_type="text/plain", content=settings.CONFIRMATION_TOKEN
        )
    await bot.process_event(data)
    return Response(media_type="text/plain", content="ok")
