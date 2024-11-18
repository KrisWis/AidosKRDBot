from aiogram import types
from InstanceBot import router, bot
from utils import adminFutureConcertsText, globalText
from keyboards import adminKeyboards
from aiogram.fsm.context import FSMContext
from database.orm import AsyncORM
from helpers import Paginator
import math
from states.Admin import FutureConcertsStates
from aiogram.filters import StateFilter
import datetime
from helpers.AlbumInfoProcessor import AlbumInfoProcessor
from RunBot import logger
import re


'''Предстоящие концерты'''
admin_future_concerts_paginator = Paginator()
# Отправка сообщения со всеми прошедшими концертами
async def send_future_concerts(call: types.CallbackQuery, state: FSMContext) -> None:
    future_concerts = await AsyncORM.get_future_concerts()
    data = await state.get_data()
        
    if len(future_concerts):
        prefix = "admin_future_concerts"
        items_per_page: int = 10

        async def getfutureConcertsButtonsAndAmount():
            future_concerts = await AsyncORM.get_future_concerts()

            buttons = [[types.InlineKeyboardButton(text=f"{future_concert.name}",
            callback_data=f'{prefix}|{future_concert.id}')] for future_concert in future_concerts]

            return [buttons, len(future_concerts)]
        
        paginator_kb = await admin_future_concerts_paginator.generate_paginator(adminFutureConcertsText.future_concerts_text,
        getfutureConcertsButtonsAndAmount, prefix,
        [await adminKeyboards.get_future_concert_kb_button(), 
        await adminKeyboards.get_back_to_admin_menu_kb_button()], items_per_page=items_per_page)

        if "media_group_messages_ids" in data:
            for media_group_message_id in data["media_group_messages_ids"]:
                await bot.delete_message(call.from_user.id, media_group_message_id)
                await state.clear()

        pages_amount = math.ceil(len(future_concerts) / items_per_page)
        await call.message.edit_text(f"(1/{pages_amount}) " + adminFutureConcertsText.future_concerts_text, 
                reply_markup=paginator_kb)
    else:
        await call.message.edit_text(globalText.data_notFound_text, reply_markup=await adminKeyboards.add_future_concert_kb())


# Отправка сообщения о том, чтобы администратор прислал название предстоящего концерта
async def wait_future_concert_name(call: types.CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(adminFutureConcertsText.wait_future_concert_name_text)

    await state.set_state(FutureConcertsStates.wait_name)


# Ожидание названия предстоящего концерта. Отправка сообщения о том, чтобы администратор прислал информацию о артисте предстоящего концерта
async def wait_future_concert_artist_info(message: types.Message, state: FSMContext):
    future_concert_name = message.text

    if future_concert_name:
        future_concert = await AsyncORM.get_future_concert_by_name(future_concert_name)

        if not future_concert:
            await state.update_data(future_concert_name=future_concert_name)

            await message.answer(adminFutureConcertsText.wait_future_concert_artist_info_text)

            await state.set_state(FutureConcertsStates.wait_artist_info)

        else:
            await message.answer(globalText.adding_data_error_text)
    else:
        await message.answer(globalText.data_isInvalid_text)


# Ожидание информации об артисте предстоящего концерта. Отправка сообщения о том, чтобы администратор прислал информацию о площадке предстоящего концерта
async def wait_future_concert_platform_info(message: types.Message, album: list[types.Message] = [], state: FSMContext = None):
    result = await AlbumInfoProcessor(FutureConcertsStates.wait_artist_info, state, message, album)

    if not result:
        await message.answer(globalText.data_isInvalid_text)
        return
    
    user_text = result[0]
    photo_file_ids = result[1]
    video_file_ids = result[2]

    await state.update_data(future_concert_artist_info_text=user_text)
    await state.update_data(future_concert_artist_info_photo_file_ids=photo_file_ids)
    await state.update_data(future_concert_artist_info_video_file_ids=video_file_ids)

    await message.answer(adminFutureConcertsText.wait_future_concert_platform_info_text)

    await state.set_state(FutureConcertsStates.wait_platform_info)


# Ожидание информации о площадке предстоящего концерта. Отправка сообщения о том, чтобы администратор прислал время проведения предстоящего концерта
async def wait_future_concert_holding_time(message: types.Message, album: list[types.Message] = [], state: FSMContext = None):
    result = await AlbumInfoProcessor(FutureConcertsStates.wait_platform_info, state, message, album)

    if not result:
        await message.answer(globalText.data_isInvalid_text)
        return
    
    user_text = result[0]
    photo_file_ids = result[1]
    video_file_ids = result[2]

    await state.update_data(future_concert_platform_info_text=user_text)
    await state.update_data(future_concert_platform_info_photo_file_ids=photo_file_ids)
    await state.update_data(future_concert_platform_info_video_file_ids=video_file_ids)

    await message.answer(adminFutureConcertsText.wait_future_concert_holding_time_text)

    await state.set_state(FutureConcertsStates.wait_holding_time)


# Ожидание информации о времени проведения предстоящего концерта. Отправка сообщения о том, чтобы администратор прислал стоимость билета предстоящего концерта
async def wait_future_concert_ticket_price(message: types.Message, state: FSMContext) -> None:
    future_concert_holding_time = message.text

    if re.match(r'^\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}$', future_concert_holding_time):

        future_concert_holding_time = datetime.datetime.strptime(future_concert_holding_time, '%d.%m.%Y %H:%M')
        now = datetime.datetime.now()

        if now >= future_concert_holding_time:
            await message.answer(globalText.date_inPastIsInvalid_text)
            return

        await state.update_data(future_concert_holding_time=future_concert_holding_time)
        
        await message.answer(adminFutureConcertsText.wait_future_concert_ticket_price_text)

        await state.set_state(FutureConcertsStates.wait_ticket_price)

    else:
        await message.answer(globalText.data_isInvalid_text)


# Ожидание информации о стоимости билета предстоящего концерта. Добавление предстоящего концерта в базу данных.
async def add_future_concert(message: types.Message, state: FSMContext) -> None:
    future_concert_ticket_price = message.text

    if future_concert_ticket_price.isdigit():
        future_concert_ticket_price = int(future_concert_ticket_price)
        data = await state.get_data()
        now = datetime.datetime.now()

        try:
            await AsyncORM.add_future_concert(data["future_concert_name"], now, data["future_concert_artist_info_text"], 
            data["future_concert_platform_info_text"], data["future_concert_holding_time"], future_concert_ticket_price,
            data["future_concert_artist_info_photo_file_ids"], data["future_concert_artist_info_video_file_ids"],
            data["future_concert_platform_info_photo_file_ids"], data["future_concert_platform_info_video_file_ids"])

            await message.answer(adminFutureConcertsText.add_future_concert_success_text, reply_markup=await adminKeyboards.back_to_admin_menu_kb())

            await state.clear()
        except Exception as e:
            logger.info(e)
            await message.answer(globalText.adding_data_error_text)

    else:
        await message.answer(globalText.data_isInvalid_text)
'''/Предстоящие концерты/'''


def hand_add():
    '''Предстоящие концерты'''
    router.callback_query.register(send_future_concerts, lambda c: c.data == 'admin|future_concerts')
    
    router.callback_query.register(wait_future_concert_name, lambda c: c.data == 'admin|future_concerts|add')

    router.message.register(wait_future_concert_artist_info, StateFilter(FutureConcertsStates.wait_name))

    router.message.register(wait_future_concert_platform_info, StateFilter(FutureConcertsStates.wait_artist_info))

    router.message.register(wait_future_concert_holding_time, StateFilter(FutureConcertsStates.wait_platform_info))

    router.message.register(wait_future_concert_ticket_price, StateFilter(FutureConcertsStates.wait_holding_time))

    router.message.register(add_future_concert, StateFilter(FutureConcertsStates.wait_ticket_price))
    '''/Предстоящие концерты/'''