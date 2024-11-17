from aiogram import types
from InstanceBot import router
from aiogram.filters import CommandStart, StateFilter
from utils import globalText
from keyboards import globalKeyboards
from database.orm import AsyncORM
from aiogram.fsm.context import FSMContext
import datetime
from InstanceBot import bot
from helpers import Paginator
import re

'''Глобальное'''
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


# Открытие стартового меню с кнопки "Обратно в меню"
async def start_from_kb(call: types.CallbackQuery, state: FSMContext) -> None:
    first_name = call.from_user.first_name

    await call.message.edit_text(globalText.start_menu_text.format(first_name),
    reply_markup=await globalKeyboards.start_menu_kb())

    await state.clear()
'''/Глобальное/'''


'''Прошедшие концерты'''
previous_concerts_paginator = Paginator()
# Отправка сообщения со всеми прошедшими концертами
async def send_previous_concerts(call: types.CallbackQuery) -> None:
    previous_concerts = await AsyncORM.get_previous_concerts()
        
    if len(previous_concerts):
        prefix = "previous_concerts"

        async def getPreviousConcertsButtonsAndAmount():
            previous_concerts = await AsyncORM.get_previous_concerts()

            buttons = [[types.InlineKeyboardButton(text=f"{previous_concert.name}",
            callback_data=f'{prefix}|{previous_concert.id}')] for previous_concert in previous_concerts]

            return [buttons, len(previous_concerts)]
        
        paginator_kb = await previous_concerts_paginator.generate_paginator(globalText.previous_concerts_text,
        getPreviousConcertsButtonsAndAmount, prefix)

        await call.message.edit_text(globalText.previous_concerts_text,
                reply_markup=paginator_kb)
    else:
        await call.message.edit_text(globalText.data_notFound_text)


# Отправка сообщения с информацией о прошедшем концерте
async def show_previous_concert(call: types.CallbackQuery) -> None:
    user_id = call.from_user.id
    message_id = call.message.message_id

    await bot.delete_message(user_id, message_id)

    temp = call.data.split("|")

    previous_concert_id = int(temp[1])

    previous_concert = await AsyncORM.get_previous_concert_by_id(previous_concert_id)

    if previous_concert:
        if previous_concert.photo_file_ids or previous_concert.video_file_ids:
            media_group_elements = []

            for photo_file_id in previous_concert.photo_file_ids:
                media_group_elements.append(types.InputMediaPhoto(media=photo_file_id))

            for video_file_id in previous_concert.video_file_ids:
                media_group_elements.append(types.InputMediaVideo(media=video_file_id))

            await call.message.answer_media_group(media_group_elements)

        answer_message_text = globalText.show_previous_concert_withoutText_text.format(previous_concert.name)

        if previous_concert.info_text:
            if not previous_concert.photo_file_ids and not previous_concert.video_file_ids:
                answer_message_text = globalText.show_previous_concert_text.format(previous_concert.name, previous_concert.info_text)
            else:
                answer_message_text = globalText.show_previous_concert_withImages_text.format(previous_concert.name, previous_concert.info_text)

        await call.message.answer(answer_message_text, reply_markup=await globalKeyboards.back_to_start_menu_kb())
    else:
        await call.message.answer(globalText.data_notFound_text)
'''/Прошедшие концерты/'''


def hand_add():
    '''Глобальное'''
    router.message.register(start, StateFilter("*"), CommandStart())

    router.callback_query.register(start_from_kb, lambda c: c.data == 'start')
    '''/Глобальное/'''

    '''Прошедшие концерты'''
    router.callback_query.register(send_previous_concerts, lambda c: c.data == 'start|previous_concerts')
    
    router.callback_query.register(show_previous_concert, lambda c: 
    re.match(r"^previous_concerts\|(?P<previous_concert_id>\d+)$", c.data))
    '''/Прошедшие концерты/'''