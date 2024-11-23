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


# Получение кнопки из инлайн-клавиатуры для добавления
async def get_kb_addButton(prefix: str):
    return InlineKeyboardButton(text='➕ Добавить', callback_data=f'admin|{prefix}|add')


# Получение кнопки для возвращения в меню выбора
async def get_kb_backToSelectionMenuButton(callback_data: str):
    return InlineKeyboardButton(text='🔙 Обратно в меню выбора', callback_data=callback_data)


# Инлайн-клавиатура для взаимодействия с данными
async def actions_kb(id: int, prefix: str):
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔄 Заменить', callback_data=f'{prefix}|{id}|replace')],
    [InlineKeyboardButton(text='❌ Удалить', callback_data=f'{prefix}|{id}|delete')]])

    return kb


# Инлайн-клавиатура для подтверждения/отклонения удаления данных о прошедшем концерте
async def delete_confirmation_kb(id: int, prefix: str):
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Я понимаю, удалить', callback_data=f'{prefix}|{id}|delete|yes')],
    [InlineKeyboardButton(text='Отменить удаление', callback_data=f'{prefix}|{id}|delete|no')]])

    return kb


# Инлайн-клавиатура для перехода обратно в меню выбора
async def back_to_selection_menu_kb(postfix: str):
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 Обратно в меню выбора', callback_data=f'admin|{postfix}')]])

    return kb
'''/Глобальное/'''

'''Предстоящие концерты'''
# Клавиатура для с кнопками для получения информации о предстоящем концерте
async def get_future_concert_info_kb(future_concert_id: int):
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🧑‍🎤 Информация об артисте', callback_data=f'admin|future_concerts|{future_concert_id}|artist'),
    InlineKeyboardButton(text='🎵 Информация о площадке', callback_data=f'admin|future_concerts|{future_concert_id}|platform')],
    [InlineKeyboardButton(text='🕰 Время проведения', callback_data=f'admin|future_concerts|{future_concert_id}|time'),
    InlineKeyboardButton(text='🎟 Стоимость билета', callback_data=f'admin|future_concerts|{future_concert_id}|price')],
    [InlineKeyboardButton(text='❌ Удалить всё', callback_data=f'future_concerts|{future_concert_id}|delete')],
    [InlineKeyboardButton(text='🔙 Обратно в меню', callback_data=f'admin')]])

    return kb


# Инлайн-клавиатура для взаимодействия с данными о предстоящем концерте
async def future_concert_actions_kb(future_concert_id: int, action: str):
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔄 Заменить', callback_data=f'admin|future_concerts|{future_concert_id}|replace|{action}')],
    [InlineKeyboardButton(text='🔙 Обратно в меню выбора', callback_data=f'admin_future_concerts|{future_concert_id}')]])

    return kb
'''/Предстоящие концерты/'''

'''Что нового?'''
# Инлайн-клавиатура для открытия меню выбора новостей
async def what_is_new_selection_menu_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📰 Новости команды', callback_data=f'admin|what_is_new|team_news')],
    [InlineKeyboardButton(text='🔊 Эксклюзивные треки', callback_data=f'admin|what_is_new|exclusive_tracks')],
    [InlineKeyboardButton(text='🎶 Музыка с концерта', callback_data=f'admin|what_is_new|concert_music')]])

    return kb
'''/Что нового?/'''