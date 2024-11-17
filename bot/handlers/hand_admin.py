from aiogram import types
from InstanceBot import router, bot
from aiogram.filters import Command, StateFilter
from utils import adminText, globalText
from keyboards import adminKeyboards
from filters import AdminFilter
from aiogram.fsm.context import FSMContext
from database.orm import AsyncORM
from helpers import Paginator
from states.Admin import PreviousConcertsStates
import re

'''Глобальное'''
# Отправка админ-меню при вводе "/admin"
async def admin(message: types.Message, state: FSMContext):
    first_name = message.from_user.first_name

    await message.answer(adminText.admin_menu_text.format(first_name), reply_markup=await adminKeyboards.admin_menu_kb())

    await state.clear()


# Открытие админ-меню с кнопки "Обратно в админ-меню"
async def admin_from_kb(call: types.CallbackQuery, state: FSMContext) -> None:
    first_name = call.from_user.first_name

    await call.message.edit_text(adminText.admin_menu_text.format(first_name), reply_markup=await adminKeyboards.admin_menu_kb())

    await state.clear()
'''/Глобальное/'''


'''Прошедшие концерты'''
admin_previous_concerts_paginator = Paginator()
# Отправка сообщения со всеми прошедшими концертами
async def send_previous_concerts(call: types.CallbackQuery) -> None:
    previous_concerts = await AsyncORM.get_previous_concerts()
        
    if len(previous_concerts):
        prefix = "admin_previous_concerts"

        async def getPreviousConcertsButtonsAndAmount():
            previous_concerts = await AsyncORM.get_previous_concerts()

            buttons = [[types.InlineKeyboardButton(text=f"{previous_concert.name}",
            callback_data=f'{prefix}|{previous_concert.id}')] for previous_concert in previous_concerts]

            return [buttons, len(previous_concerts)]
        
        paginator_kb = await admin_previous_concerts_paginator.generate_paginator(adminText.previous_concerts_text,
        getPreviousConcertsButtonsAndAmount, prefix, [await adminKeyboards.get_previous_concert_kb_button()])

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
    photo_file_ids = []
    video_file_ids = []

    data = await state.get_data()

    if photo or video or len(album) or user_text:

        if not len(album):
            if photo:
                photo = photo[-1]
                photo_file_ids.append(photo.file_id)

            if video:
                video_file_ids.append(video.file_id)
        else:
            for element in album:
                if element.caption:
                    user_text = element.caption

                if element.photo:
                    photo_file_ids.append(element.photo[-1].file_id)

                elif element.video:
                    video_file_ids.append(element.video.file_id)

                else:
                    current_state = await state.get_state()

                    if current_state == PreviousConcertsStates.wait_info:
                        await message.answer(globalText.data_isInvalid_text)

        current_state = await state.get_state()

        if current_state == PreviousConcertsStates.wait_info:
            await state.set_state(None)

            if "previous_concert_replace_id" in data:
                previous_concert_replace_id = int(data["previous_concert_replace_id"])

                await AsyncORM.change_previousConcert_info(previous_concert_replace_id,
                user_text, photo_file_ids, video_file_ids)

                previous_concert = await AsyncORM.get_previous_concert_by_id(previous_concert_replace_id)

                await message.answer(adminText.change_previous_concert_success_text.format(previous_concert.name), reply_markup=await adminKeyboards.back_to_admin_menu_kb())
            else:
                await AsyncORM.add_previous_concert(data["previous_concert_name"], user_text, photo_file_ids, video_file_ids)

                await message.answer(adminText.add_previous_concert_success_text, reply_markup=await adminKeyboards.back_to_admin_menu_kb())

    else:
        current_state = await state.get_state()

        if current_state == PreviousConcertsStates.wait_info:
            await message.answer(globalText.data_isInvalid_text)


# Отправка сообщения с информацией о прошедшем концерте и возможностью удаления/изменения информации
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

        answer_message_text = adminText.show_previous_concert_withoutText_text.format(previous_concert.name)

        if previous_concert.info_text:
            if not previous_concert.photo_file_ids and not previous_concert.video_file_ids:
                answer_message_text = adminText.show_previous_concert_text.format(previous_concert.name, previous_concert.info_text)
            else:
                answer_message_text = adminText.show_previous_concert_withImages_text.format(previous_concert.name, previous_concert.info_text)

        await call.message.answer(answer_message_text,
        reply_markup=await adminKeyboards.previous_concert_actions_kb(previous_concert.id))
    else:
        await call.message.answer(globalText.data_notFound_text)


# Обработка изменения/удаления информации о прошедшем концерте
async def previous_concert_actions(call: types.CallbackQuery, state: FSMContext) -> None:

    temp = call.data.split("|")

    previous_concert_id = int(temp[1])

    action = temp[2]

    previous_concert = await AsyncORM.get_previous_concert_by_id(previous_concert_id)

    if not previous_concert:
        await call.message.answer(globalText.data_notFound_text)
        return
    
    if action == "replace":
        await call.message.edit_text(adminText.previous_concert_actions_edit_text)
        await state.update_data(previous_concert_replace_id=previous_concert_id)

        await state.set_state(PreviousConcertsStates.wait_info)

    elif action == "delete":
        await call.message.edit_text(adminText.previous_concert_actions_delete_confirmation_text.
        format(previous_concert.name),
        reply_markup=await adminKeyboards.previous_concert_delete_confirmation_kb(previous_concert.id))


# Обработка подтверждения/отклонения удаления информации о прошедшем концерте
async def previous_concert_delete_confirmation(call: types.CallbackQuery) -> None:

    temp = call.data.split("|")

    previous_concert_id = int(temp[1])

    action = temp[3]

    previous_concert = await AsyncORM.get_previous_concert_by_id(previous_concert_id)

    if not previous_concert:
        await call.message.answer(globalText.data_notFound_text)
        return
    
    if action == "yes":
        await AsyncORM.delete_previous_concert(previous_concert_id)

        await call.message.edit_text(adminText.previous_concert_actions_delete_confirmation_yes_text.
        format(previous_concert.name), reply_markup=await adminKeyboards.back_to_admin_menu_kb())

    elif action == "no":
        await call.message.edit_text(adminText.previous_concert_actions_delete_confirmation_no_text.
        format(previous_concert.name), reply_markup=await adminKeyboards.back_to_admin_menu_kb())

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

    router.callback_query.register(show_previous_concert, lambda c: 
    re.match(r"^admin_previous_concerts\|(?P<previous_concert_id>\d+)$", c.data))

    router.callback_query.register(previous_concert_actions, lambda c: 
    re.match(r"^previous_concerts\|(?P<previous_concert_id>\d+)\|(?P<action>replace|delete)$", c.data))

    router.callback_query.register(previous_concert_delete_confirmation, lambda c: 
    re.match(r"^previous_concerts\|(?P<previous_concert_id>\d+)\|delete\|(?P<choice>yes|no)$", c.data))
    '''/Прошедшие концерты/'''