from aiogram.types import InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from utils import globalTexts
from typing import Callable, Union, Awaitable
from helpers import Paginator
from InstanceBot import bot
import math


# Отправка сообщения с пагинацией в зависимости от входных данных
async def sendPaginationMessage(call: CallbackQuery, state: FSMContext, items: list,
    getButtonsAndAmount: Callable[[], Awaitable[Union[list[InlineKeyboardButton], int]]],
    prefix: str, text: str, items_per_page: int = 10,
    extra_buttons: list[InlineKeyboardButton] = [], extra_button_beforeActionsButtons: bool = True) -> None:
    data = await state.get_data()
        
    if len(items):

        paginator = Paginator()
        
        paginator_kb = await paginator.generate_paginator(text,
        getButtonsAndAmount, prefix, extra_buttons,
        items_per_page=items_per_page, extra_button_beforeActionsButtons=extra_button_beforeActionsButtons)

        if "media_group_messages_ids" in data:
            for media_group_message_id in data["media_group_messages_ids"]:
                await bot.delete_message(call.from_user.id, media_group_message_id)
                await state.clear()

        pages_amount = math.ceil(len(items) / items_per_page)
        await call.message.edit_text(f"(1/{pages_amount}) " + text,
                reply_markup=paginator_kb)
    else:
        await call.message.edit_text(globalTexts.data_notFound_text)