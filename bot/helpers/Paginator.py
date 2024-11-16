from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import math
from InstanceBot import router
import re


# Класс для функционала пагинации
class Paginator:
    # Генерация клавиатуры вместе с добавлением хендлера
    async def generate_paginator(self, text: str, items_amount: int, 
        buttons: list[InlineKeyboardButton], prefix: str, extra_buttons: list[InlineKeyboardButton] = [], items_per_page: int = 10) -> InlineKeyboardMarkup:
        
        paginator_kb = await self.paginator(items_amount, buttons, prefix, extra_buttons, items_per_page=items_per_page)

        await self.page_action_paginator_handler_registrator(text, items_amount, buttons, prefix, items_per_page)

        return paginator_kb
    

    # Инлайн-клавиатура для пагинации
    @staticmethod
    async def paginator(items_amount: int, buttons: list[InlineKeyboardButton], prefix: str,
        extra_buttons: list[InlineKeyboardButton] = [], current_page_index: int = 0, items_per_page: int = 10) -> InlineKeyboardMarkup:
        inline_keyboard = []

        pages_amount = math.ceil(items_amount / items_per_page)

        pages = [buttons[i:i + items_per_page] for i in range(0, len(buttons), items_per_page)]

        for _, page in enumerate(pages[current_page_index], start=1):
            for button in page:
                inline_keyboard.append([button])

        action_kb_buttons = []

        if current_page_index > 0:
            action_kb_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"{prefix}|page|{current_page_index}|prev"))

        if pages_amount > 1 and current_page_index < pages_amount - 1:
            action_kb_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"{prefix}|page|{current_page_index}|next"))

        if len(action_kb_buttons):
            inline_keyboard.append(action_kb_buttons)

        for extra_button in extra_buttons:
            inline_keyboard.append([extra_button])

        kb = InlineKeyboardMarkup(
        inline_keyboard=inline_keyboard)

        return kb
    

    # Хендлер для обработки страниц
    async def page_action_paginator_handler_registrator(self, text: str, items_amount: int, 
        buttons: list[InlineKeyboardButton], prefix: str, items_per_page: int = 10) -> None:
        async def page_action_paginator_handler(call: CallbackQuery) -> None:
            temp = call.data.split("|")

            page = temp[2]

            action = temp[3]

            if action == "next":
                page = int(page) + 1

            elif action == "prev":
                page = int(page) - 1

            pages_amount = math.ceil(len(items_amount) / items_per_page)

            await call.message.edit_text(f"({page}/{pages_amount})" + text, 
            reply_markup=self.paginator(items_amount, buttons, prefix, page, items_per_page))
            
        router.callback_query.register(page_action_paginator_handler,
        lambda c: 
        re.match(r'^(?P<prefix>[^|]+)\|page\|(?P<current_page_index>\d+)\|(?P<action>prev|next)$', c.data))
