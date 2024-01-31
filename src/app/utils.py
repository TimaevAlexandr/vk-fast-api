from vkbottle.user import Message

import settings
from app.db.groups import get_groups_ids
from app.db.admins import get_all_admins, get_all_superusers
from app.db.faculties import get_faculty_id

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


async def handle_faculty(message: Message, text: str, faculty: str) -> tuple[int | None, str | None, bool | None]:
    if faculty =="суперадмин":
        return None, None, True

    elif faculty in ("РТС", "ИКСС", "ИСиТ", "ФФП", "ЦЭУБИ", "СЦТ", "ИНО", "ИМ", "СПБКТ", "ВУЦ"):
        faculty_id = get_faculty_id(faculty)
        is_superuser = False
        return faculty_id, None, is_superuser
    
    else:
        await message.answer(text)
        return None, text, None
    


async def handle_admin_id(
    message: Message, admin_id: str | int, check: bool = False
) -> bool:

    super_admins = await get_all_superusers()
    if message.from_id not in super_admins:
        await message.answer("не достаточно прав")
        return False

    if not isinstance(admin_id, int):
        await message.answer("Не верно введён id админа!")
        return False

    all_admins = await get_all_admins()
    if admin_id in all_admins:
        await message.answer("Такой админ уже существует!")
        return False

    if check:
        groups_ids = await get_groups_ids()

        if not groups_ids:
            await message.answer("Произошла непредвиденная ошибка!")
            return False

    return True