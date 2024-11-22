from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


'''Глобальное'''
# Инлайн-клавиатура для начального меню
async def start_menu_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='◀️ Прошедшие концерты', callback_data='start|previous_concerts'),
    InlineKeyboardButton(text='▶️ Предстоящие концерты', callback_data='start|future_concerts')],
    [InlineKeyboardButton(text='ℹ️ О нас', callback_data='start|about_us'),
    InlineKeyboardButton(text='❓ Что нового?', callback_data='start|what_is_new')],
    [InlineKeyboardButton(text='👥 Наши партнёры', callback_data='start|out_partners')],
    [InlineKeyboardButton(text='📊 Статистика', callback_data='start|stats')]])

    return kb


# Инлайн-клавиатура для перехода обратно в меню прошедших концертов
async def back_to_previous_concerts_menu_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 Обратно в меню выбора', callback_data='start|previous_concerts')]])

    return kb


# Получение кнопки из инлайн-клавиатуры для перехода обратно в начальное меню
async def get_back_to_start_menu_kb_button():
    return InlineKeyboardButton(text='🔙 Обратно в меню', callback_data='start')

'''/Глобальное/'''


'''Предстоящие концерты'''
# Клавиатура для с кнопками для получения информации о предстоящем концерте
async def get_future_concert_info_kb(future_concert_id: int):
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🧑‍🎤 Информация об артисте', callback_data=f'start|future_concerts|{future_concert_id}|artist'),
    InlineKeyboardButton(text='🎵 Информация о площадке', callback_data=f'start|future_concerts|{future_concert_id}|platform')],
    [InlineKeyboardButton(text='🕰 Время проведения', callback_data=f'start|future_concerts|{future_concert_id}|time'),
    InlineKeyboardButton(text='🎟 Стоимость билета', callback_data=f'start|future_concerts|{future_concert_id}|price')],
    [InlineKeyboardButton(text='🔙 Обратно в меню', callback_data=f'start')]])

    return kb


# Инлайн-клавиатура для возврата обратно в меню выбора
async def back_to_future_concert_selection_menu_kb(future_concert_id: int):
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 Обратно в меню выбора', callback_data=f'future_concerts|{future_concert_id}')]])

    return kb
'''/Предстоящие концерты/'''

'''О нас'''
# Инлайн-клавиатура для выбора того, какую информацию хотите получить
async def about_us_choice_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='ℹ️ О нас', callback_data='start|about_us|about_us')],
    [InlineKeyboardButton(text='🎼 О организации', callback_data='start|about_us|about_organization')],
    [InlineKeyboardButton(text='🔙 Назад', callback_data='start')]])

    return kb


# Инлайн-клавиатура для возврата обратно в меню выбора информации
async def back_to_about_us_selection_menu_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 Обратно в меню выбора', callback_data='start|about_us')]])

    return kb
'''/О нас/'''

'''Что нового?'''
# Инлайн-клавиатура для открытия меню выбора новостей
async def what_is_new_selection_menu_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📰 Новости команды', callback_data=f'start|what_is_new|team_news')],
    [InlineKeyboardButton(text='🔊 Эксклюзивные треки', callback_data=f'start|what_is_new|exclusive')],
    [InlineKeyboardButton(text='🎶 Музыка с концерта', callback_data=f'start|what_is_new|music')]])

    return kb


# Получение кнопки для возвращения в меню выбора новостей
async def get_team_news_kb_backToSelectionMenuButton():
    return InlineKeyboardButton(text='🔙 Обратно в меню выбора', callback_data='start|what_is_new')


# Инлайн-клавиатура для возврата обратно в меню выбора новости
async def back_to_team_news_selection_menu_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 Обратно в меню выбора', callback_data='start|what_is_new|team_news')]])

    return kb
'''/Что нового?/'''