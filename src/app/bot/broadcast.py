import logging
import re
from app.db.groups import get_group_faculty_id, is_group_of_admin
from app.utils import get_group_id

from vkbottle.bot import BotLabeler
from vkbottle.user import Message as VKMessage

import settings
from app.broadcast import broadcast
from app.db.admins import get_admin_by_id, get_all_admins

logger = logging.getLogger(__name__)

broadcast_labeler = BotLabeler()
broadcast_labeler.vbml_ignore_case = True


regex = r"[Рр]ассылка:\s*((?:\d+\s*)+)\s*(?:([А-Яа-я\s]+))?\.\s*([\s\S]*)$"
regex_all = r"[Рр]ассылка:\s*всем\s*\.\s*([\s\S]*)"


def get_results(broadcast_result):
    if not broadcast_result:
        return None
    results = []
    for course, course_result, faculty_name in broadcast_result:
        course_arr = [f"Курс {course} факультет {faculty_name}:"]
        for group in course_result:
            if group:
                course_arr.append("+")
            else:
                course_arr.append("-")
        results.append(" ".join(course_arr))
    return "\n".join(results)


def get_text(message: VKMessage, text: str | None) -> str | None:
    if message.fwd_messages:
        logger.info(f"Found forward message: {message.fwd_messages[0].text}")
        return "\n\n".join(
            fwd_message.text for fwd_message in message.fwd_messages
        )
    if message.reply_message:
        logger.info(f"Found reply message: {message.reply_message.text}")
        return str(message.reply_message.text)
    logger.info("Did not found forward message")
    return text


def get_attachments(message: VKMessage) -> str | None:
    attachments = message.get_wall_attachment()
    if attachments:
        logger.info(f"Found attachments: {attachments[0]}")
        return f"wall{attachments[0].owner_id}_{attachments[0].id}"
    return None


def parse_text(message: VKMessage) -> tuple[str, str | None, str]:
    res = re.match(regex, message.text)
    res_all = re.match(regex_all, message.text)
    if not res and not res_all:
        raise ValueError("Wrong regex text")
    elif not res:
        courses = "всем"
        faculties = ""
        text = res_all.group(1)  # type: ignore
    elif not res_all:
        courses, faculties, text = res.groups()
    else:
        raise ValueError("Wrong regex text")
    return (
        courses.strip(),
        faculties.strip() if faculties else None,
        text.strip(),
    )


@broadcast_labeler.message(regex=regex)
@broadcast_labeler.message(regex=regex_all)
async def sharing_text(message: VKMessage) -> None:
    group_id = get_group_id(message)
    if not is_group_of_admin(group_id):
        return

    group_faculty_id = await get_group_faculty_id(group_id)
    sender = await get_admin_by_id(message.from_id)

    if not sender:
        return

    if sender.faculty_id != group_faculty_id:
        await message.answer("Это беседа для админов другого факультета")
        return
    courses, faculties, text = parse_text(message)

    _text = get_text(message, text)
    _attachment = get_attachments(message)

    if not _text and not _attachment:
        await message.answer("Нечего пересылать")
        return

    broadcast_result = await broadcast(
        courses,
        faculties,
        message.from_id,
        text=_text,
        attachment=[_attachment] if _attachment else None,
    )

    if broadcast_result:
        if "+" in get_results(broadcast_result) and "-" not in get_results(
            broadcast_result
        ):
            text_answer = "Рассылка успешно отправлена!"
        elif "+" in get_results(broadcast_result):
            text_answer = "Рассылка отправлена не полностью."
        else:
            text_answer = "Не удалось отправить рассылку."
    else:
        text_answer = "Не удалось отправить рассылку."
    ouptut_result = get_results(broadcast_result)

    if ouptut_result:
        await message.answer(f"{text_answer}\n\n{ouptut_result}")
    else:
        await message.answer(f"{text_answer}")
