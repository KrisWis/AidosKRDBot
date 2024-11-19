import asyncio
from typing import Any, Awaitable, Callable, Dict, List, Union
from aiogram import BaseMiddleware
from aiogram.types import (
    Message,
    TelegramObject,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from InstanceBot import dp, bot
from states.Admin import PreviousConcertsStates, FutureConcertsStates

DEFAULT_DELAY = 1.5

class MediaGroupMiddleware(BaseMiddleware):
    ALBUM_DATA: Dict[str, List[Message]] = {}

    def __init__(self, delay: Union[int, float] = DEFAULT_DELAY):
        self.delay = delay

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id

        state_with: FSMContext = FSMContext(
            storage=dp.storage,
            key=StorageKey(
                chat_id=user_id,
                user_id=user_id,  
                bot_id=bot.id))
        
        current_state = await state_with.get_state()

        if not event.media_group_id:
            if current_state in [PreviousConcertsStates.wait_info, FutureConcertsStates.wait_artist_info, FutureConcertsStates.wait_platform_info]:
                await asyncio.sleep(self.delay)
            
            return await handler(event, data)

        try:
            self.ALBUM_DATA[event.media_group_id].append(event)
            return 
        except KeyError:
            self.ALBUM_DATA[event.media_group_id] = [event]
            await asyncio.sleep(self.delay)
            data["album"] = self.ALBUM_DATA.pop(event.media_group_id)

        return await handler(event, data)