from vkbottle.user import Message

import settings
from app.db import get_groups_ids


def process_course(course: str | int) -> int:
    if course == "admin":
        return -1
    if isinstance(course, int):
        return course
    if isinstance(course, str) and course.isnumeric():
        return int(course)
    return 0


async def handle_course(
    message: Message, course: str | int, check: bool = False
) -> bool:
    _course = process_course(course)

    if _course not in (-1, 1, 2, 3, 4, 5):
        await message.answer("Не верно введен курс!")
        return False

    if check:
        groups_ids = await get_groups_ids()

        if not groups_ids:
            await message.answer("Произошла непредвиденная ошибка!")
            return False

    return True


async def handle_group(
    message: Message, text: str
) -> tuple[int | None, str | None]:
    group_id: int = message.peer_id - settings.GROUP_ID_COEFFICIENT
    groups_ids = await get_groups_ids()

    if group_id in groups_ids:
        await message.answer(text)
        return None, text
    return group_id, None
