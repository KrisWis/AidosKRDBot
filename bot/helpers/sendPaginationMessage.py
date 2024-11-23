from aiogram.types import InlineKeyboardButton, CallbackQuery, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from utils import globalTexts
from typing import Callable, Union, Awaitable
from helpers import Paginator
import math
from helpers.deleteSendedMediaGroup import deleteSendedMediaGroup
from helpers.deleteMessage import deleteMessage


# Отправка сообщения с пагинацией в зависимости от входных данных
async def sendPaginationMessage(call: CallbackQuery, state: FSMContext, items: list,
    getButtonsAndAmount: Callable[[], Awaitable[Union[list[InlineKeyboardButton], int]]],
    prefix: str, text: str, items_per_page: int = 10,
    extra_buttons: list[InlineKeyboardButton] = [], extra_button_beforeActionsButtons: bool = True) -> None:
    await deleteMessage(call)
    
    if len(items):

        paginator = Paginator()
        
        paginator_kb = await paginator.generate_paginator(text,
        getButtonsAndAmount, prefix, extra_buttons,
        items_per_page=items_per_page, extra_button_beforeActionsButtons=extra_button_beforeActionsButtons)

        await deleteSendedMediaGroup(state, call.from_user.id)

        pages_amount = math.ceil(len(items) / items_per_page)
        await call.message.answer(f"(1/{pages_amount}) " + text,
                reply_markup=paginator_kb)
    else:
        inline_keyboard = []

        for extra_button in extra_buttons:
            inline_keyboard.append([extra_button])

        kb = InlineKeyboardMarkup(
        inline_keyboard=inline_keyboard)

        await call.message.answer(globalTexts.data_notFound_text, reply_markup=kb)