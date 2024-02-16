import asyncio
import logging
from datetime import datetime
from typing import Coroutine

import aiohttp
from vkbottle import VKAPIError

import settings
from app.db.admins import get_admin_by_id
from app.db.faculties import get_faculty_name
from app.db.groups import (
    connect_message_to_group,
    delete_group,
    get_group_ids_by_course_faculty_id,
    get_groups_ids,
)
from app.exceptions import DBError
from app.utils import make_pairs, proc_course
from app.vk import bot

logger = logging.getLogger(__name__)


async def group_broadcast(
    group: int, text: str | None, attachment: list | None
) -> bool:
    try:
        await bot.api.messages.send(
            peer_id=(settings.GROUP_ID_COEFFICIENT + group),
            message=text,
            attachment=attachment,
            random_id=0,
        )
    except VKAPIError[7] as exception:
        logger.warning(exception)
        await delete_group(group)
    except VKAPIError as exception:
        logger.error(exception)
    except aiohttp.ClientConnectorError as exception:
        logger.exception(exception)
    else:
        return True
    return False


async def course_broadcast(
    course: int,
    from_id: int,
    text: str | None,
    attachment: list | None,
    faculty_id: int,
) -> tuple[int, tuple[bool], str]:
    faculty_name = await get_faculty_name(faculty_id)
    try:
        ids = await get_group_ids_by_course_faculty_id(course, faculty_id)
        
    except DBError as error:
        logger.error(error)
        return course, (False,), faculty_name

    if not ids:
        return course, (False,), faculty_name

    result: list[bool] = []
    for group in ids:
        res = await group_broadcast(group, text, attachment)
        result.append(res)
        await connect_message_to_group(
            group, text, attachment, datetime.now(), from_id, res
        )
    return course, tuple(result), faculty_name  # type: ignore[return-value]


async def all_groups_broadcast(
    from_id: int,
    text: str | None,
    attachment: list | None,
):
    try:
        all_groups_ids = await get_groups_ids()
    except DBError as error:
        logger.error(error)
        return "не найден", (False,), "не найден"

    result: list[bool] = []
    for group_id in all_groups_ids:
        res = await group_broadcast(group_id, text, attachment)
        result.append(res)
        print(group_id)
        await connect_message_to_group(
            group_id, text, attachment, datetime.now(), from_id, res
        )
    return "ВСЕ", tuple(result), "ВСЕ"  # type: ignore[return-value]


async def broadcast(
    courses: str,
    faculties: str | None,
    from_id: int,
    text: str | None = None,
    attachment: list | None = None,
) -> tuple[tuple[int, tuple[bool]]] | None:
    try:
        admin = await get_admin_by_id(int(from_id))
        if not admin:
            return None

        coroutines: list[Coroutine] = []

        processed_courses = await proc_course(courses)
        if not processed_courses and courses != "всем":
            logger.error("Courses is not valid")
            return None

        if admin.is_superuser:
            # Суперпользователь
            if courses == "всем":
                coroutines.append(
                    all_groups_broadcast(admin.id, text, attachment)
                )
            else:
                for course, faculty_id in await make_pairs(
                    processed_courses, faculties
                ):
                    coroutines.append(
                        course_broadcast(
                            int(course), from_id, text, attachment, faculty_id
                        )
                    )
        else:
            # Обычный администратор
            for course in sorted(processed_courses):
                coroutines.append(
                    course_broadcast(
                        int(course),
                        from_id,
                        text,
                        attachment,
                        admin.faculty_id,
                    )
                )

        done = await asyncio.gather(*coroutines)
        return tuple(done)  # type: ignore[return-value]
    except DBError as error:
        logger.error(error)
        return None
