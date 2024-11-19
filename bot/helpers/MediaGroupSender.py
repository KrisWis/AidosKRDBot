from aiogram import types
from aiogram.fsm.context import FSMContext


async def MediaGroupSender(call: types.CallbackQuery, state: FSMContext, photo_file_ids: list[str], video_file_ids: list[str]) -> bool:
    if photo_file_ids or video_file_ids:

        media_group_elements = []

        for photo_file_id in photo_file_ids:
            media_group_elements.append(types.InputMediaPhoto(media=photo_file_id))

        for video_file_id in video_file_ids:
            media_group_elements.append(types.InputMediaVideo(media=video_file_id))

        media_group_messages = await call.message.answer_media_group(media_group_elements)

        await state.update_data(media_group_messages_ids=[media_group_message.message_id for media_group_message in media_group_messages])
        
    return True