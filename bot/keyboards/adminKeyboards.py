from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

'''Глобальное'''
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


# Инлайн-клавиатура для перехода обратно в админ-меню
async def back_to_admin_menu_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 Обратно в админ-меню', callback_data='admin')]])

    return kb


# Получение кнопки из инлайн-клавиатуры для перехода обратно в админ-меню
async def get_back_to_admin_menu_kb_button():
    return InlineKeyboardButton(text='🔙 Обратно в админ-меню', callback_data='admin')
'''/Глобальное/'''


'''Прошедшие концерты'''
# Получение кнопки из инлайн-клавиатуры для добавления прошедшего концерта
async def get_previous_concert_kb_button():
    return InlineKeyboardButton(text='➕ Добавить концерт', callback_data='admin|previous_concerts|add')


# Инлайн-клавиатура для добавления прошедшего концерта
async def add_previous_concert_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [await get_previous_concert_kb_button()]])

    return kb

# Инлайн-клавиатура для взаимодействия с данными о прошедшем концерте
async def previous_concert_actions_kb(previous_concert_kb: int):
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔄 Заменить', callback_data=f'previous_concerts|{previous_concert_kb}|replace')],
    [InlineKeyboardButton(text='❌ Удалить', callback_data=f'previous_concerts|{previous_concert_kb}|delete')]])

    return kb


# Инлайн-клавиатура для подтверждения/отклонения удаления данных о прошедшем концерте
async def previous_concert_delete_confirmation_kb(previous_concert_kb: int):
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Я понимаю, удалить', callback_data=f'previous_concerts|{previous_concert_kb}|delete|yes')],
    [InlineKeyboardButton(text='Отменить удаление', callback_data=f'previous_concerts|{previous_concert_kb}|delete|no')]])

    return kb


# Инлайн-клавиатура для перехода обратно в меню прошедших концертов
async def back_to_previous_concerts_menu_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 Обратно в меню выбора', callback_data='admin|previous_concerts')]])

    return kb
'''/Прошедшие концерты/'''

'''Предстоящие концерты'''
# Клавиатура для с кнопками для получения информации о предстоящем концерте
async def get_future_concert_info_kb(future_concert_id: int):
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🧑‍🎤 Информация об артисте', callback_data=f'admin|future_concerts|{future_concert_id}|artist'),
    InlineKeyboardButton(text='🎵 Информация о площадке', callback_data=f'admin|future_concerts|{future_concert_id}|platform')],
    [InlineKeyboardButton(text='🕰 Время проведения', callback_data=f'admin|future_concerts|{future_concert_id}|time'),
    InlineKeyboardButton(text='🎟 Стоимость билета', callback_data=f'admin|future_concerts|{future_concert_id}|price')],
    [InlineKeyboardButton(text='❌ Удалить всё', callback_data=f'future_concerts|{future_concert_id}|delete')]])

    return kb


# Получение кнопки из инлайн-клавиатуры для добавления предстоящего концерта
async def get_future_concert_kb_button():
    return InlineKeyboardButton(text='➕ Добавить концерт', callback_data='admin|future_concerts|add')


# Инлайн-клавиатура для добавления предстоящего концерта
async def add_future_concert_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [await get_future_concert_kb_button()]])

    return kb


# Инлайн-клавиатура для взаимодействия с данными о предстоящем концерте
async def future_concert_actions_kb(future_concert_id: int, action: str):
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔄 Заменить', callback_data=f'admin|future_concerts|{future_concert_id}|replace|{action}')],
    [InlineKeyboardButton(text='🔙 Обратно в меню выбора', callback_data=f'admin_future_concerts|{future_concert_id}')]])

    return kb


# Инлайн-клавиатура для подтверждения/отклонения удаления данных о предстоящем концерте
async def future_concert_delete_confirmation_kb(future_concert_id: int):
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Я понимаю, удалить', callback_data=f'future_concerts|{future_concert_id}|delete|yes')],
    [InlineKeyboardButton(text='Отменить удаление', callback_data=f'future_concerts|{future_concert_id}|delete|no')]])

    return kb


# Инлайн-клавиатура для перехода обратно в меню предстоящих концертов
async def back_to_future_concerts_menu_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 Обратно в меню выбора', callback_data='admin|future_concerts')]])

    return kb
'''/Предстоящие концерты/'''