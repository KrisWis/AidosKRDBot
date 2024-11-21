from aiogram.fsm.context import FSMContext
from InstanceBot import bot


async def deleteSendedMediaGroup(state: FSMContext, user_id: int):
    data = await state.get_data()

    if "media_group_messages_ids" in data:
        for media_group_message_id in data["media_group_messages_ids"]:
            await bot.delete_message(user_id, media_group_message_id)
            await state.clear()