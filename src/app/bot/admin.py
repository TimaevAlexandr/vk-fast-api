from vkbottle.bot import BotLabeler
from vkbottle.user import Message

from app.bot import messages
from app.db.admins import add_admin, delete_admin
from app.db.groups import add_group, change_group_course
from app.utils import (
    handle_admin_id,
    handle_course,
    handle_faculty,
    handle_group,
)


admin_labeler = BotLabeler()
admin_labeler.vbml_ignore_case = True


@admin_labeler.message(text="Изменить курс <course>")
async def change_course(message: Message, course: str) -> None:
    if not await handle_course(message, course, check=True):
        return

    group_id, err = await handle_group(message, messages.NO_CHAT)
    if err:
        return

    await change_group_course(group_id, course)

    await message.answer(messages.EDITED_SUCCESSFULLY % {"course": course})


@admin_labeler.message(text="Добавить <course> <faculty>")
async def add(message: Message, course: str, faculty: str) -> None:
    if not await handle_course(message, course):
        return

    group_id, err = await handle_group(
        message, "Ваша беседа уже есть в списке"
    )
    
    if err:
        return
    
    faculty_id, err, is_superuser = await handle_faculty(
        message, f"Факультет {faculty} не найден", faculty
    )
    if err:
        return

    await add_group(group_id, int(course), faculty_id)

    await message.answer(messages.ADDED_SUCCESSFULLY % {"course": course})
    await message.answer(messages.WELCOME % {"course": course})


# функционал для суперадмина + того кто прописан в settings.py

@admin_labeler.message(text="Создать администратора <admin_id> <faculty>")
async def add_faculty_admin(
    message: Message, admin_id: str, faculty: str
) -> None:
    admin_id_validated = await handle_admin_id(message, admin_id, need_in_table=False)
    if not isinstance(admin_id_validated, int):
        return

    faculty_id, err, is_superuser = await handle_faculty(
        message, f"Факультет {faculty} не найден", faculty
    )

    if err:
        return

    await add_admin(admin_id_validated, is_superuser, faculty_id)

    if not is_superuser:
        await message.answer(
            messages.ADDED_ADMIN_SUCCESSFULLY.format(admin_id=admin_id_validated, faculty=faculty)
        )
    else:
        await message.answer(
            messages.ADDED_SUPER_ADMIN_SUCCESSFULLY.format(admin_id=admin_id_validated)
        )

@admin_labeler.message(text="Удалить администратора <admin_id>")
async def delete_faculty_admin(message: Message, admin_id: str) -> None:
    admin_id_validated = await handle_admin_id(message, admin_id, need_in_table=True)
    if not isinstance(admin_id_validated, int):
        return

    await delete_admin(admin_id_validated)

    await message.answer(
            messages.ADMIN_DELETED_SUCCESSFULLY.format(admin_id=admin_id_validated)
        )