from aiogram import types
from InstanceBot import router
from aiogram.filters import Command, StateFilter
from utils import adminTexts
from keyboards import adminKeyboards
from filters import AdminFilter
from aiogram.fsm.context import FSMContext


'''Глобальное'''
# Отправка админ-меню при вводе "/admin"
async def admin(message: types.Message, state: FSMContext):
    first_name = message.from_user.first_name

    await message.answer(adminTexts.admin_menu_text.format(first_name), reply_markup=await adminKeyboards.admin_menu_kb())

    await state.clear()


# Открытие админ-меню с кнопки "Обратно в админ-меню"
async def admin_from_kb(call: types.CallbackQuery, state: FSMContext) -> None:
    first_name = call.from_user.first_name

    await call.message.edit_text(adminTexts.admin_menu_text.format(first_name), reply_markup=await adminKeyboards.admin_menu_kb())

    await state.clear()
'''/Глобальное/'''


def hand_add():
    '''Глобальное'''
    router.message.register(admin, StateFilter("*"), Command("admin"), AdminFilter())

    router.callback_query.register(admin_from_kb, lambda c: c.data == 'admin')
    '''/Глобальное/'''