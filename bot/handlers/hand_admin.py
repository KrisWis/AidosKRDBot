from aiogram import types
from InstanceBot import router
from aiogram.filters import Command, StateFilter
from utils import adminText, globalText
from keyboards import adminKeyboards
from Config import admins


# Отправка админ-меню при вводе "/admin"
async def admin(message: types.Message):
    user_id = message.from_user.id

    if user_id in admins:
        await message.answer(adminText.admin_menu_text, reply_markup=adminKeyboards.admin_menu_kb())
    else:
        await message.answer(globalText.rightsError_text)

def hand_add():
    router.message.register(admin, StateFilter("*"), Command("admin"))
