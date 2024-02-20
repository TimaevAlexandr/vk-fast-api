import re

from vkbottle.user import Message

import settings
from app.db.admins import Admin, get_all_admins, get_all_superusers
from app.db.faculties import get_faculty_id
from app.db.groups import get_groups_ids
from settings import ADMINS

all_courses = (-1, 1, 2, 3, 4, 5)


def is_valid_id_format(input_string):
    pattern = r"\[id\d+\|.+?\]"
    return bool(re.match(pattern, input_string))


def extract_id(input_string):
    pattern = r"\[id(\d+)\|.+?\]"
    match = re.match(pattern, input_string)
    if match:
        return match.group(1)
    else:
        return None


def process_course(course: str | int) -> int:
    if course == "admin":
        return -1
    if isinstance(course, int):
        return course
    if isinstance(course, str) and course.isnumeric():
        return int(course)
    return 0


async def make_pairs(courses: set, faculties: str | None):
    if -1 in courses:
        courses.remove(-1)  # исключаем админский курс
    crs = sorted(courses)

    if not faculties:
        return [(course, None) for course in crs]

    fac_list = faculties.split(" ")
    
    fac_ids = [await get_faculty_id(faculty.strip()) for faculty in fac_list if faculty]

    pairs = [(course, faculty_id) for course in crs for faculty_id in fac_ids]

    return pairs


def parse_add_regex(
    message: Message,
) -> tuple[str | None, str | None] | tuple[None, None]:
    add_pattern = re.compile(r"^Добавить (\S+)(?:\s*([^\[\]]+))?$")
    match = add_pattern.match(message.text)

    if match:
        course = match.group(1)
        faculty = match.group(2)
        return course, faculty
    else:
        return None, None


async def proc_course(courses):
    processed_courses = set()
    for cours in set(courses):
        _course = process_course(cours.strip())

        if _course not in all_courses:
            continue
        processed_courses.add(_course)
    return processed_courses


async def handle_course(
    message: Message, course: str | int, check: bool = False
) -> int:
    _course = process_course(course)

    if _course not in all_courses:
        await message.answer("Не верно введен курс!")
        return False

    if check:
        groups_ids = await get_groups_ids()

        if not groups_ids:
            await message.answer("Произошла непредвиденная ошибка!")
            return False

    return _course


def get_group_id(message: Message) -> int:
    return int(message.peer_id) - settings.GROUP_ID_COEFFICIENT


async def handle_faculty(
    message: Message, text: str, faculty: str
) -> tuple[int | None, str | None, bool | None]:
    if faculty == "суперадмин":
        return None, None, True

    else:
        faculty_id = await get_faculty_id(faculty)
        if faculty_id:
            is_superuser = False
            return faculty_id, None, is_superuser
        else:
            await message.answer(text)
            return None, text, None


async def handle_admin_id(
    message: Message, admin_id: str, need_in_table: bool
) -> int | bool:
    super_admins = await get_all_superusers() + ADMINS

    if message.from_id not in super_admins:
        await message.answer("Не достаточно прав")
        return False

    if not is_valid_id_format(admin_id):
        await message.answer(
            "Не верно введён id админа! (необходимо указывать @...)"
        )
        return False

    admin_id_int = int(extract_id(admin_id))

    if (
        not need_in_table
    ):  # если необходимо условие что такой не должен быть в таблице
        # для добавления админа
        all_admins: list[Admin] = await get_all_admins()

        if any(int(admin.id) == admin_id_int for admin in all_admins):
            await message.answer("Такой админ уже существует!")
            return False

    return admin_id_int

async def group_is_added(group_id: int) -> bool:
    return group_id in await get_groups_ids()

