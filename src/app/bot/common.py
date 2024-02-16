from vkbottle.bot import BotLabeler
from vkbottle.user import Message
from vkbottle_types.objects import MessagesSendUserIdsResponseItem

import settings
from app.bot import messages
from app.db.admins import get_all_admins, get_all_superusers

common_labeler = BotLabeler()
common_labeler.vbml_ignore_case = True


@common_labeler.message(text="Помощь")
async def user_help(message: Message) -> MessagesSendUserIdsResponseItem:
    all_admins = await get_all_admins()
    if not all_admins:
        return
    all_admins_id = [admin.id for admin in all_admins] + settings.ADMINS

    if message.from_id not in all_admins_id:
        return await message.answer(messages.FORBIDDEN)

    return await message.answer(messages.HELP)


@common_labeler.message(text="Список факультетов")
async def faculty_list(message: Message) -> MessagesSendUserIdsResponseItem:
    all_superusers = await get_all_superusers()
    if not all_superusers:
        return
    all_superusers_ids = [
        super.id for super in all_superusers
    ] + settings.ADMINS
    if message.from_id not in all_superusers_ids:
        return await message.answer(messages.FORBIDDEN)

    return await message.answer(messages.FacultiesMessage)
