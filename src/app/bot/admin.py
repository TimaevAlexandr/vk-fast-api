import re

from vkbottle.bot import BotLabeler
from vkbottle.user import Message as VKMessage

import settings
from app.bot import messages
from app.db import count_messages
from app.db.admins import add_admin, archive_admin, Admin, get_admin_by_id, get_all_superusers, restore_admin
from app.db.groups import (
    add_group,
    change_group_course,
    get_course_by_group_id,
    group_is_added,
    is_group_of_admin,
)
from app.utils import (
    get_group_id,
    handle_admin_id,
    handle_course,
    handle_faculty,
    get_group_id,
)

admin_labeler = BotLabeler()
admin_labeler.vbml_ignore_case = True


def parse_statistics_text(message: VKMessage) -> str | None:
    res = re.match(regex, message.text)
    if not res:
        raise ValueError("Wrong regex text")
    (course,) = res.groups()
    return course


regex = r"[Сс]татистика(?: (\d))?"
@admin_labeler.message(regex=regex)
async def statistics(message: VKMessage) -> None:
    course = parse_statistics_text(message)
    if course is not None and not await handle_course(message, course):
        return

    answer: list[str] = []
    current_course = None

    for _course, group, count_received, count_all in await count_messages():
        if course is None or _course == int(course):
            if current_course != _course:
                answer.append(f"{_course} курс - {count_all} сообщений:")
                current_course = _course
            answer.append(f"Группа {group}: {count_received}/{count_all}")

    await message.answer("\n".join(answer))


@admin_labeler.message(text="Изменить курс <course>")
async def change_course(message: VKMessage, course: str) -> None:
    if not await handle_course(message, course, check=True):
        return

    group_id = get_group_id(message)
    if not await group_is_added(group_id):
        await message.answer("Вашей беседы ещё нет в списке")
        return

    if int(course) == await get_course_by_group_id(group_id):
        await message.answer("Группе уже присвоен %s курс" % course)
        return

    await change_group_course(group_id, int(course))

    await message.answer(messages.EDITED_SUCCESSFULLY % {"course": course})


@admin_labeler.message(text="Добавить <course> <faculty>")
async def add(message: VKMessage, course: str, faculty: str) -> None:
    is_admin = False
    _course = await handle_course(message, course)  # type: ignore
    if not _course:
        return

    group_id = get_group_id(message)

    if await group_is_added(group_id):
        await message.answer("Ваша беседа уже есть в списке")
        return


    if faculty:
        faculty_id, err, is_superuser = await handle_faculty(
            message, f"Факультет {faculty} не найден", faculty
        )
        if err:
            return
    else:
        # беседа супер админов
        faculty_id = None

    if _course == -1:
        _course = None
        is_admin = True
    
    
    await add_group(group_id, int(_course), faculty_id, is_admin)

    if _course:
        await message.answer(messages.ADDED_SUCCESSFULLY % {"course": _course})
        await message.answer(messages.WELCOME % {"course": _course})


# функционал для суперадмина(бд) + того кто прописан в settings.py


@admin_labeler.message(text="Создать администратора <admin_id> <faculty>")
async def add_faculty_admin(
    message: VKMessage, admin_id: str, faculty: str
) -> None:
    group_id = get_group_id(message)
    if not is_group_of_admin(group_id):
        return

    admin_id_validated = await handle_admin_id(
        message, admin_id, need_in_table=False
    )
    if not admin_id_validated:
        return

    faculty_id, err, is_superuser = await handle_faculty(
        message, f"Факультет {faculty} не найден", faculty
    )

    if err:
        return

    if isinstance(admin_id_validated, int):
        await add_admin(admin_id_validated, is_superuser, faculty_id, is_archived=False)
    elif isinstance(admin_id_validated, Admin): # in db but archived case
        await restore_admin(admin_id_validated.id)

    if not is_superuser:
        await message.answer(
            messages.ADDED_ADMIN_SUCCESSFULLY.format(
                admin_id=admin_id_validated, faculty=faculty
            )
        )
    else:
        await message.answer(
            messages.ADDED_SUPER_ADMIN_SUCCESSFULLY.format(
                admin_id=admin_id_validated
            )
        )


@admin_labeler.message(text="Удалить администратора <admin_id>")
async def delete_faculty_admin(message: VKMessage, admin_id: str) -> None:
    
    group_id = get_group_id(message)
    if not is_group_of_admin(group_id):
        return

    admin_id_validated = await handle_admin_id(
        message, admin_id, need_in_table=True
    )
    if not isinstance(admin_id_validated, int):
        return

    await archive_admin(admin_id_validated) # переносим в архив

    await message.answer(
        messages.ADMIN_DELETED_SUCCESSFULLY.format(admin_id=admin_id_validated)
    )
