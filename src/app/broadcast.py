import asyncio
import logging
from typing import Coroutine

import aiohttp
from vkbottle import VKAPIError

import settings
from app.db.groups import (
    delete_group,
    get_group_ids_by_course,
    connect_message_to_group,
)
from app.db.messages import add_message, Message
from app.exceptions import DBError
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
    message_id: int,
    text: str | None,
    attachment: list | None,
) -> tuple[int, tuple[bool]]:
    try:
        ids = await get_group_ids_by_course(course)
    except DBError as error:
        logger.error(error)
        return course, (False,)

    if not ids:
        return course, (False,)

    result: list[bool] = []
    for group in ids:
        res = await group_broadcast(group, text, attachment)
        result.append(res)
        await connect_message_to_group(group, message_id, res)
    return course, tuple(result)  # type: ignore[return-value]


async def broadcast(
    courses: str,
    from_id: int,
    text: str | None = None,
    attachment: list | None = None,
) -> tuple[tuple[int, tuple[bool]]] | None:
    if not courses.isnumeric():
        logger.error("Courses is not numeric")
        return None
    coroutines: list[Coroutine] = []
    message_id = await add_message(text, attachment, from_id)
    for course in sorted(set(courses)):
        coroutines.append(
            course_broadcast(int(course), message_id, text, attachment)
        )
    done = await asyncio.gather(*coroutines)
    return tuple(done)  # type: ignore[return-value]
