
from database.orm import AsyncORM
from aiogram.types import Message
from RunBot import logger
from utils import globalTexts
from typing import Callable, Awaitable, Dict, Any
from keyboards import adminKeyboards
from aiogram.fsm.context import FSMContext


async def futureConcertChangeInfo(data: Dict[str, Any], state: FSMContext, message: Message,
    changeInfo: Callable[[int], Awaitable[None]], text: str) -> bool:

    if "future_concert_replace_id" in data:
        future_concert_replace_id = int(data["future_concert_replace_id"])

        future_concert = await AsyncORM.get_future_concert_by_id(future_concert_replace_id)

        try:
            await changeInfo(future_concert_replace_id)
        except Exception as e:
            logger.info(e)
            await message.answer(globalTexts.adding_data_error_text)
            return True

        await message.answer(text.format(future_concert.name), 
        reply_markup=await adminKeyboards.back_to_admin_menu_kb())
        await state.clear()
        return True
    
    return False