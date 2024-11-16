from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# Инлайн-клавиатура для начального меню
async def start_menu_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='◀️ Прошедшие концерты', callback_data='start|previous_concerts'),
    InlineKeyboardButton(text='▶️ Предстоящие концерты', callback_data='start|future_concerts')],
    [InlineKeyboardButton(text='ℹ️ О нас', callback_data='start|discounts'),
    InlineKeyboardButton(text='❓ Что нового?', callback_data='start|what_is_new')],
    [InlineKeyboardButton(text='👥 Наши партнёры', callback_data='start|out_partners')],
    [InlineKeyboardButton(text='📊 Статистика', callback_data='start|stats')]])

    return kb