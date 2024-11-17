from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import math
from InstanceBot import router
import re
from typing import Callable, Union, Awaitable


# Класс для функционала пагинации
class Paginator:

    def __init__(self):
        self.handler_is_registered = False

    # Генерация клавиатуры вместе с добавлением хендлера
    async def generate_paginator(self, text: str,
        getButtonsAndAmount: Callable[[], Awaitable[Union[list[InlineKeyboardButton], int]]],
        prefix: str, extra_buttons: list[InlineKeyboardButton] = [], items_per_page: int = 10) -> InlineKeyboardMarkup:
        
        paginator_kb = await self.paginator(getButtonsAndAmount, prefix, extra_buttons, items_per_page=items_per_page)

        if not self.handler_is_registered:
            await self.page_action_paginator_handler_registrator(text, getButtonsAndAmount, prefix, extra_buttons, items_per_page)
            self.handler_is_registered = True

        return paginator_kb
    

    # Инлайн-клавиатура для пагинации
    @staticmethod
    async def paginator(getButtonsAndAmount: Callable[[], Awaitable[Union[list[InlineKeyboardButton], int]]],
        prefix: str,
        extra_buttons: list[InlineKeyboardButton] = [], current_page_index: int = 0, items_per_page: int = 10) -> InlineKeyboardMarkup:
        inline_keyboard = []

        buttonsAndAmount = await getButtonsAndAmount()
        items_amount = buttonsAndAmount[1]
        
        pages_amount = math.ceil(items_amount / items_per_page)

        buttons = buttonsAndAmount[0]
        
        pages = [buttons[i:i + items_per_page] for i in range(0, len(buttons), items_per_page)]

        for _, page in enumerate(pages[current_page_index], start=1):
            for button in page:
                inline_keyboard.append([button])

        action_kb_buttons = []

        if current_page_index > 0:
            action_kb_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"{prefix}|page|{current_page_index}|prev"))

        if pages_amount > 1 and current_page_index < pages_amount - 1:
            action_kb_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"{prefix}|page|{current_page_index}|next"))

        for extra_button in extra_buttons:
            inline_keyboard.append([extra_button])

        if len(action_kb_buttons):
            inline_keyboard.append(action_kb_buttons)

        kb = InlineKeyboardMarkup(
        inline_keyboard=inline_keyboard)

        return kb
    

    # Хендлер для обработки страниц
    async def page_action_paginator_handler_registrator(self, text: str,
        getButtonsAndAmount: Callable[[], Awaitable[Union[list[InlineKeyboardButton], int]]],
        prefix: str, extra_buttons: list[InlineKeyboardButton] = [], items_per_page: int = 10) -> None:
        async def page_action_paginator_handler(call: CallbackQuery) -> None:

            buttonsAndAmount = await getButtonsAndAmount()
            items_amount = buttonsAndAmount[1]

            temp = call.data.split("|")

            page = temp[2]

            action = temp[3]

            if action == "next":
                page = int(page) + 1

            elif action == "prev":
                page = int(page) - 1

            pages_amount = math.ceil(items_amount / items_per_page)

            await call.message.edit_text(f"({page + 1}/{pages_amount}) " + text, 
            reply_markup=await self.paginator(getButtonsAndAmount, prefix, extra_buttons, current_page_index=page, items_per_page=items_per_page))
            
        router.callback_query.register(page_action_paginator_handler,
        lambda c: 
        re.match(r'^(?P<prefix>[^|]+)\|page\|(?P<current_page_index>\d+)\|(?P<action>prev|next)$', c.data))
