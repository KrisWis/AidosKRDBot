from aiogram.types import Message
from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext
from utils import globalText
from typing import Union

async def AlbumInfoProcessor(current_state: State, state: FSMContext, message: Message,
    album: list[Message] = []) -> Union[str, list[str], list[str]]:
    user_text = message.text or message.caption or ""

    photo = message.photo
    video = message.video
    photo_file_ids = []
    video_file_ids = []

    if not photo and not video and not len(album) and message.caption:
        await message.answer(globalText.data_isInvalid_text)
            
        return False
    
    if photo or video or len(album) or user_text:

        if not len(album):
            if photo:
                photo = photo[-1]
                photo_file_ids.append(photo.file_id)

            if video:
                video_file_ids.append(video.file_id)
        else:
            for element in album:
                if element.caption:
                    user_text = element.caption

                if element.photo:
                    photo_file_ids.append(element.photo[-1].file_id)

                elif element.video:
                    video_file_ids.append(element.video.file_id)

                else:
                    current_state = await state.get_state()

                    if current_state == current_state:
                        await message.answer(globalText.data_isInvalid_text)

                    return False

        current_state = await state.get_state()

        if current_state == current_state:
            await state.set_state(None)

            return [user_text, photo_file_ids, video_file_ids]
    else:
        current_state = await state.get_state()

        if current_state == current_state:
            await message.answer(globalText.data_isInvalid_text)
            
    return False
    