from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# Инлайн-клавиатура для админ-меню
async def admin_menu_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='◀️ Прошедшие концерты', callback_data='admin|previous_concerts'),
    InlineKeyboardButton(text='▶️ Предстоящие концерты', callback_data='admin|future_concerts')],
    [InlineKeyboardButton(text='❓ Что нового?', callback_data='admin|what_is_new'),
    InlineKeyboardButton(text='💲 Скидки и акции', callback_data='admin|discounts')],
    [InlineKeyboardButton(text='👥 Наши партнёры', callback_data='admin|out_partners')],
    [InlineKeyboardButton(text='📊 Статистика', callback_data='admin|stats')]])

    return kb


'''Прошедшие концерты'''
# Получение кнопки из инлайн-клавиатуры для добавления прошедшего концерта
async def get_previous_concert_kb_button():
    return [InlineKeyboardButton(text='➕ Добавить концерт', callback_data='admin|previous_concerts|add')]


# Инлайн-клавиатура для добавления прошедшего концерта
async def add_previous_concert_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [await get_previous_concert_kb_button()]])

    return kb
'''/Прошедшие концерты/'''