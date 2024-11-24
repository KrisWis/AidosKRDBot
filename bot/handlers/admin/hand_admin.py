from aiogram import types
from InstanceBot import router
from aiogram.filters import Command, StateFilter
from utils import adminTexts, globalTexts
from keyboards import adminKeyboards
from filters import AdminFilter
from aiogram.fsm.context import FSMContext
from helpers import deleteSendedMediaGroup
from database.orm import AsyncORM
from states.Admin import StatsStates
import re


'''Глобальное'''
# Отправка админ-меню при вводе "/admin"
async def admin(message: types.Message, state: FSMContext):
    await deleteSendedMediaGroup(state, message.from_user.id)
    
    first_name = message.from_user.first_name

    await message.answer(adminTexts.admin_menu_text.format(first_name), reply_markup=await adminKeyboards.admin_menu_kb())

    await state.clear()


# Открытие админ-меню с кнопки "Обратно в админ-меню"
async def admin_from_kb(call: types.CallbackQuery, state: FSMContext) -> None:
    first_name = call.from_user.first_name

    await call.message.edit_text(adminTexts.admin_menu_text.format(first_name), reply_markup=await adminKeyboards.admin_menu_kb())

    await state.clear()
'''/Глобальное/'''


'''Статистика'''
# Отправка сообщения с выбором времени статистики
async def send_stats_selection(call: types.CallbackQuery):
    await call.message.edit_text(
        text=adminTexts.stats_title_text,
        reply_markup=adminKeyboards.select_stats_period_kb()
    )


# Обработка клавиатуры со статистикой
async def send_stats(call: types.CallbackQuery):
    temp = call.data.split('|')

    all_users = await AsyncORM.get_all_users(period=temp[1])

    geo = await AsyncORM.get_all_users(period=temp[1], geo=True)

    temp_dict = {
        "day": "день",
        "week": "неделю",
        "month": "месяц",
        "all": "всё время",
    }

    await call.message.edit_text(
        text=adminTexts.stats_info_text.format(temp_dict[temp[1]], len(all_users), geo),
        reply_markup=adminKeyboards.select_stats_period_kb()
    )


# Отправка сообщения с текстом того, чтобы администратор отправил id пользователя, по которому хочет узнать статистику
async def wait_user_id_for_stats(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        text=adminTexts.wait_user_id_for_stats_text
    )

    await state.set_state(StatsStates.wait_user_id)


# Ожидание Telegram ID пользователя. Отправка сообщения со статистикой пользователя
async def send_user_individual_stats(message: types.Message, state: FSMContext):
    user_id = message.text

    if user_id.isdigit():

        user_id = int(user_id)

        user = await AsyncORM.get_user(user_id)

        if user:

            user_reg_date = user.user_reg_date.strftime("%d.%m.%Y %H:%M")

            user_referals = await AsyncORM.get_user_referals(user_id)

            await message.answer(adminTexts.send_user_individual_stats_text
            .format(user.username, user_id, user_reg_date, len(user_referals)),
            reply_markup=await adminKeyboards.back_to_selection_menu_kb('stats'))

            await state.clear()
            return

    await message.answer(globalTexts.data_isInvalid_text)
'''/Статистика/'''


def hand_add():
    '''Глобальное'''
    router.message.register(admin, StateFilter("*"), Command("admin"), AdminFilter())

    router.callback_query.register(admin_from_kb, lambda c: c.data == 'admin')
    '''/Глобальное/'''

    '''Статистика'''
    router.callback_query.register(send_stats_selection, lambda c: c.data == 'admin|stats')

    router.callback_query.register(send_stats, lambda c: re.match(r"stats\|(day|week|month|all)", c.data))

    router.callback_query.register(wait_user_id_for_stats, lambda c: c.data == 'stats|individual')

    router.message.register(send_user_individual_stats, StateFilter(StatsStates.wait_user_id))
    '''/Статистика/'''