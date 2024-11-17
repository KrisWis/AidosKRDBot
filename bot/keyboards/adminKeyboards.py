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
'''/Глобальное/'''


'''Прошедшие концерты'''
# Получение кнопки из инлайн-клавиатуры для добавления прошедшего концерта
async def get_previous_concert_kb_button():
    return [InlineKeyboardButton(text='➕ Добавить концерт', callback_data='admin|previous_concerts|add')]


# Инлайн-клавиатура для добавления прошедшего концерта
async def add_previous_concert_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
    await get_previous_concert_kb_button()])

    return kb


# Инлайн-клавиатура для перехода обратно в админ-меню
async def back_to_admin_menu_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 Обратно в админ-меню', callback_data='admin')]])

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
'''/Прошедшие концерты/'''