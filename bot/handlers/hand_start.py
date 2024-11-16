from aiogram import types
from InstanceBot import router
from aiogram.filters import CommandStart, StateFilter
from utils import globalText
from keyboards import globalKeyboards
from database.orm import AsyncORM
from aiogram.fsm.context import FSMContext
import datetime
from InstanceBot import bot


# Отправка стартового меню при вводе "/start"
async def start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username
    now = datetime.datetime.now()
    
    if not await AsyncORM.get_user(user_id):
        referer_id = message.text[7:] or None

        if referer_id:
            if referer_id.isdigit() and referer_id != str(user_id):

                await bot.send_message(
                    chat_id=referer_id,
                    text=globalText.new_referal_text.format(username)
                )

                referer_id = int(referer_id)  

        result = await AsyncORM.add_user(
            user_id,
            username,
            now,
            message.from_user.language_code,
            referer_id
        )

        if not result:
            await message.answer(globalText.adding_data_error_text)
            return

    await message.answer(globalText.start_menu_text.format(first_name), 
                reply_markup=await globalKeyboards.start_menu_kb())
    await state.clear()


def hand_add():
    router.message.register(start, StateFilter("*"), CommandStart())