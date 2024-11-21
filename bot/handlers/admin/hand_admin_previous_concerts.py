from aiogram import types
from InstanceBot import router, bot
from aiogram.filters import StateFilter
from utils import globalTexts, adminPreviousConcertsTexts
from keyboards import adminKeyboards
from aiogram.fsm.context import FSMContext
from database.orm import AsyncORM
from states.Admin import PreviousConcertsStates
import re
import datetime
from helpers import albumInfoProcess, mediaGroupSend, sendPaginationMessage
from RunBot import logger


'''Прошедшие концерты'''
# Отправка сообщения со всеми прошедшими концертами
async def send_previous_concerts(call: types.CallbackQuery, state: FSMContext) -> None:
    previous_concerts = await AsyncORM.get_previous_concerts()
    prefix = "admin_previous_concerts"

    async def getPreviousConcertsButtonsAndAmount():
        previous_concerts = await AsyncORM.get_previous_concerts()

        buttons = [[types.InlineKeyboardButton(text=f"{previous_concert.name}",
        callback_data=f'{prefix}|{previous_concert.id}')] for previous_concert in previous_concerts]

        return [buttons, len(previous_concerts)]
    
    await sendPaginationMessage(call, state, previous_concerts, getPreviousConcertsButtonsAndAmount,
    prefix, adminPreviousConcertsTexts.previous_concerts_text, 10,
    [await adminKeyboards.get_previous_concert_kb_button(), 
    await adminKeyboards.get_back_to_admin_menu_kb_button()])


# Отправка сообщения о том, чтобы администратор прислал название прошедшего концерта
async def wait_previous_concert_name(call: types.CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(adminPreviousConcertsTexts.wait_previous_concert_name_text)

    await state.set_state(PreviousConcertsStates.wait_name)


# Ожидание названия предстоящего концерта. Отправка сообщения о том, чтобы администратор прислал информацию о прошедшем концерте
async def wait_previous_concert_info(message: types.Message, state: FSMContext):
    previous_concert_name = message.text

    if previous_concert_name:
        previous_concert = await AsyncORM.get_previous_concert_by_name(previous_concert_name)

        if not previous_concert:
            await state.update_data(previous_concert_name=previous_concert_name)

            await message.answer(adminPreviousConcertsTexts.wait_previous_concert_info_text)

            await state.set_state(PreviousConcertsStates.wait_info)

        else:
            await message.answer(globalTexts.adding_data_error_text)
    else:
        await message.answer(globalTexts.data_isInvalid_text)


# Ожидание информации предстоящего концерта. Добавление прошедшего концерта в базу данных
async def add_previous_concert(message: types.Message, album: list[types.Message] = [], state: FSMContext = None):
    result = await albumInfoProcess(PreviousConcertsStates.wait_info, state, message, album)

    if not result:
        await message.answer(globalTexts.data_isInvalid_text)
        return

    user_text = result[0]
    photo_file_ids = result[1]
    video_file_ids = result[2]
    now = datetime.datetime.now()
    data = await state.get_data()

    if "previous_concert_replace_id" in data:
        previous_concert_replace_id = int(data["previous_concert_replace_id"])

        await AsyncORM.change_previousConcert_info(previous_concert_replace_id,
        user_text, photo_file_ids, video_file_ids)

        previous_concert = await AsyncORM.get_previous_concert_by_id(previous_concert_replace_id)

        await message.answer(adminPreviousConcertsTexts.change_previous_concert_success_text.format(previous_concert.name), reply_markup=await adminKeyboards.back_to_admin_menu_kb())
    else:
        try:
            await AsyncORM.add_previous_concert(data["previous_concert_name"], user_text, now, photo_file_ids, video_file_ids)

            await message.answer(adminPreviousConcertsTexts.add_previous_concert_success_text, reply_markup=await adminKeyboards.back_to_admin_menu_kb())
        except Exception as e:
            logger.info(e)
            await message.answer(globalTexts.adding_data_error_text)

    await state.clear()


# Отправка сообщения с информацией о прошедшем концерте и возможностью удаления/изменения информации
async def show_previous_concert(call: types.CallbackQuery, state: FSMContext) -> None:
    user_id = call.from_user.id
    message_id = call.message.message_id

    await bot.delete_message(user_id, message_id)

    temp = call.data.split("|")

    previous_concert_id = int(temp[1])

    previous_concert = await AsyncORM.get_previous_concert_by_id(previous_concert_id)

    if previous_concert:
        await mediaGroupSend(call, state, previous_concert.photo_file_ids, previous_concert.video_file_ids)

        answer_message_text = adminPreviousConcertsTexts.show_previous_concert_withoutText_text.format(previous_concert.name)

        if previous_concert.info_text:
            if not previous_concert.photo_file_ids and not previous_concert.video_file_ids:
                answer_message_text = adminPreviousConcertsTexts.show_previous_concert_text.format(previous_concert.name, previous_concert.info_text)
            else:
                answer_message_text = adminPreviousConcertsTexts.show_previous_concert_withImages_text.format(previous_concert.name, previous_concert.info_text)

        await call.message.answer(answer_message_text,
        reply_markup=await adminKeyboards.actions_kb(previous_concert.id, 'previous_concerts'))
    else:
        await call.message.answer(globalTexts.data_notFound_text)


# Обработка изменения/удаления информации о прошедшем концерте
async def previous_concert_actions(call: types.CallbackQuery, state: FSMContext) -> None:

    temp = call.data.split("|")

    previous_concert_id = int(temp[1])

    action = temp[2]

    previous_concert = await AsyncORM.get_previous_concert_by_id(previous_concert_id)

    if not previous_concert:
        await call.message.answer(globalTexts.data_notFound_text)
        return
    
    if action == "replace":
        await call.message.edit_text(adminPreviousConcertsTexts.previous_concert_actions_edit_text)
        await state.update_data(previous_concert_replace_id=previous_concert_id)

        await state.set_state(PreviousConcertsStates.wait_info)

    elif action == "delete":
        await call.message.edit_text(adminPreviousConcertsTexts.previous_concert_actions_delete_confirmation_text.
        format(previous_concert.name),
        reply_markup=await adminKeyboards.delete_confirmation_kb(previous_concert.id, 'previous_concerts'))


# Обработка подтверждения/отклонения удаления информации о прошедшем концерте
async def previous_concert_delete_confirmation(call: types.CallbackQuery) -> None:

    temp = call.data.split("|")

    previous_concert_id = int(temp[1])

    action = temp[3]

    previous_concert = await AsyncORM.get_previous_concert_by_id(previous_concert_id)

    if not previous_concert:
        await call.message.answer(globalTexts.data_notFound_text)
        return
    
    if action == "yes":
        await AsyncORM.delete_previous_concert(previous_concert_id)

        await call.message.edit_text(adminPreviousConcertsTexts.previous_concert_actions_delete_confirmation_yes_text.
        format(previous_concert.name), reply_markup=await adminKeyboards.back_to_selection_menu_kb('previous_concerts'))

    elif action == "no":
        await call.message.edit_text(adminPreviousConcertsTexts.previous_concert_actions_delete_confirmation_no_text.
        format(previous_concert.name), reply_markup=await adminKeyboards.back_to_selection_menu_kb('previous_concerts'))
'''/Прошедшие концерты/'''


def hand_add():
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