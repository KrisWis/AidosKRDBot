from aiogram import types
from InstanceBot import router
from aiogram.filters import Command, StateFilter
from utils import adminText, globalText
from keyboards import adminKeyboards
from filters import AdminFilter
from aiogram.fsm.context import FSMContext
from database.orm import AsyncORM
from helpers import Paginator
import math
from states.Admin import PreviousConcertsStates
from typing import Union


paginator = Paginator()

'''Глобальное'''
# Отправка админ-меню при вводе "/admin"
async def admin(message: types.Message, state: FSMContext):
    await message.answer(adminText.admin_menu_text, reply_markup=await adminKeyboards.admin_menu_kb())

    await state.clear()


# Открытие админ-меню с кнопки "Назад в админ меню"
async def admin_from_kb(call: types.CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(adminText.admin_menu_text, reply_markup=await adminKeyboards.admin_menu_kb())

    await state.clear()
'''/Глобальное/'''


'''Прошедшие концерты'''
# Отправка сообщения со всеми прошедшими концертами
async def send_previous_concerts(call: types.CallbackQuery) -> None:
    previous_concerts = await AsyncORM.get_previous_concerts()
        
    if len(previous_concerts):
        prefix = "previous_concerts"

        async def getPreviousConcertsButtonsAndAmount() -> Union[list[types.InlineKeyboardButton], int]:
            previous_concerts = await AsyncORM.get_previous_concerts()

            buttons = [[types.InlineKeyboardButton(text=f"{previous_concert.name}",
            callback_data=f'{prefix}|{previous_concert.id}')] for previous_concert in previous_concerts]

            return [buttons, len(previous_concerts)]
        
        paginator_kb = await paginator.generate_paginator(adminText.previous_concerts_text,
        getPreviousConcertsButtonsAndAmount, prefix, await adminKeyboards.get_previous_concert_kb_button())

        await call.message.edit_text(adminText.previous_concerts_text, 
                reply_markup=paginator_kb)
    else:
        await call.message.edit_text(globalText.data_notFound_text, reply_markup=await adminKeyboards.add_previous_concert_kb())


# Отправка сообщения о том, чтобы администратор прислал название прошедшего концерта
async def wait_previous_concert_name(call: types.CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(adminText.wait_previous_concert_name_text)

    await state.set_state(PreviousConcertsStates.wait_name)


# Отправка сообщения о том, чтобы администратор прислал информацию о прошедшем концерте
async def wait_previous_concert_info(message: types.Message, state: FSMContext):
    previous_concert_name = message.text

    if previous_concert_name:
        previous_concert = await AsyncORM.get_previous_concert_by_name(previous_concert_name)

        if not previous_concert:
            await state.update_data(previous_concert_name=previous_concert_name)

            await message.answer(adminText.wait_previous_concert_info_text)

            await state.set_state(PreviousConcertsStates.wait_info)

        else:
            await message.answer(globalText.adding_data_error_text)
    else:
        await message.answer(globalText.data_isInvalid_text)


# Добавление прошедшего концерта в базу данных
async def add_previous_concert(message: types.Message, album: list[types.Message] = [], state: FSMContext = None):
    user_text = message.text or message.caption or ""

    photo = message.photo
    video = message.video
    media_group_id = message.media_group_id
    info_file_ids = []

    data = await state.get_data()

    if photo or video or media_group_id or user_text:

        if photo:
            photo = photo[-1]
            info_file_ids.append(photo.file_id)

        if video:
            info_file_ids.append(video.file_id)

        for element in album:
            if element.caption:
                user_text = element.caption

            if element.photo:
                info_file_ids.append(element.photo[-1].file_id)

            elif element.video:
                info_file_ids.append(element.video.file_id)

            else:
                current_state = await state.get_state()

                if current_state == PreviousConcertsStates.wait_info:
                    await message.answer(globalText.data_isInvalid_text)

        current_state = await state.get_state()

        if current_state == PreviousConcertsStates.wait_info:
            await state.set_state(None)
            await AsyncORM.add_previous_concert(data["previous_concert_name"], user_text, info_file_ids)

            await message.answer(adminText.add_previous_concert_success_text, reply_markup=await adminKeyboards.back_to_admin_menu_kb())

    else:
        current_state = await state.get_state()

        if current_state == PreviousConcertsStates.wait_info:
            await message.answer(globalText.data_isInvalid_text)

'''/Прошедшие концерты/'''


def hand_add():
    '''Глобальное'''
    router.message.register(admin, StateFilter("*"), Command("admin"), AdminFilter())

    router.callback_query.register(admin_from_kb, lambda c: c.data == 'admin')
    '''/Глобальное/'''

    '''Прошедшие концерты'''
    router.callback_query.register(send_previous_concerts, lambda c: c.data == 'admin|previous_concerts')

    router.callback_query.register(wait_previous_concert_name, lambda c: c.data == 'admin|previous_concerts|add')

    router.message.register(wait_previous_concert_info, StateFilter(PreviousConcertsStates.wait_name))

    router.message.register(add_previous_concert, StateFilter(PreviousConcertsStates.wait_info))
    '''/Прошедшие концерты/'''