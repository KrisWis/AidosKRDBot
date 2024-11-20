from aiogram import types
from InstanceBot import router
from aiogram.filters import CommandStart, StateFilter
from utils import globalTexts, userPreviousConcertsTexts, userFutureConcertsTexts
from keyboards import globalKeyboards
from database.orm import AsyncORM
from aiogram.fsm.context import FSMContext
import datetime
from InstanceBot import bot
from helpers import Paginator, mediaGroupSend, sendPaginationMessage
import re
import math


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
                    text=globalTexts.new_referal_text.format(username)
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
            await message.answer(globalTexts.adding_data_error_text)
            return

    await message.answer(globalTexts.start_menu_text.format(first_name), 
                reply_markup=await globalKeyboards.start_menu_kb())
    await state.clear()


# Открытие стартового меню с кнопки "Обратно в меню"
async def start_from_kb(call: types.CallbackQuery, state: FSMContext) -> None:
    first_name = call.from_user.first_name

    await call.message.edit_text(globalTexts.start_menu_text.format(first_name),
    reply_markup=await globalKeyboards.start_menu_kb())

    await state.clear()
'''/Глобальное/'''


'''Прошедшие концерты'''
# Отправка сообщения со всеми прошедшими концертами
async def send_previous_concerts(call: types.CallbackQuery, state: FSMContext) -> None:
    previous_concerts = await AsyncORM.get_previous_concerts()
    prefix = "previous_concerts"

    async def getPreviousConcertsButtonsAndAmount():
        previous_concerts = await AsyncORM.get_previous_concerts()

        buttons = [[types.InlineKeyboardButton(text=f"{previous_concert.name}",
        callback_data=f'{prefix}|{previous_concert.id}')] for previous_concert in previous_concerts]

        return [buttons, len(previous_concerts)]
    
    await sendPaginationMessage(call, state, previous_concerts, getPreviousConcertsButtonsAndAmount,
    prefix, userPreviousConcertsTexts.previous_concerts_text, 10, [await globalKeyboards.get_back_to_start_menu_kb_button()],
    False)


# Отправка сообщения с информацией о прошедшем концерте
async def show_previous_concert(call: types.CallbackQuery, state: FSMContext) -> None:
    user_id = call.from_user.id
    message_id = call.message.message_id

    await bot.delete_message(user_id, message_id)

    temp = call.data.split("|")

    previous_concert_id = int(temp[1])

    previous_concert = await AsyncORM.get_previous_concert_by_id(previous_concert_id)

    if previous_concert:
        await mediaGroupSend(call, state, previous_concert.photo_file_ids, previous_concert.video_file_ids)

        answer_message_text = userPreviousConcertsTexts.show_previous_concert_withoutText_text.format(previous_concert.name)

        if previous_concert.info_text:
            if not previous_concert.photo_file_ids and not previous_concert.video_file_ids:
                answer_message_text = userPreviousConcertsTexts.show_previous_concert_text.format(previous_concert.name, previous_concert.info_text)
            else:
                answer_message_text = userPreviousConcertsTexts.show_previous_concert_withImages_text.format(previous_concert.name, previous_concert.info_text)

        await call.message.answer(answer_message_text, reply_markup=await globalKeyboards.back_to_previous_concerts_menu_kb())
    else:
        await call.message.answer(userPreviousConcertsTexts.data_notFound_text)
'''/Прошедшие концерты/'''


'''Предстоящие концерты'''
# Отправка сообщения со всеми предстоящими концертами
async def send_future_concerts(call: types.CallbackQuery, state: FSMContext) -> None:

    future_concerts = await AsyncORM.get_future_concerts()
    prefix = "future_concerts"

    async def getFutureConcertsButtonsAndAmount():
        future_concerts = await AsyncORM.get_future_concerts()

        buttons = [[types.InlineKeyboardButton(
        text=f"{future_concert.name if len(future_concert.name) <= 35 else future_concert.name[:35] + '...'} — {future_concert.holding_time.strftime("%d.%m.%Y %H:%M")}",
        callback_data=f'{prefix}|{future_concert.id}')] for future_concert in future_concerts]

        return [buttons, len(future_concerts)]
    
    await sendPaginationMessage(call, state, future_concerts, getFutureConcertsButtonsAndAmount,
    prefix, userFutureConcertsTexts.future_concerts_text, 10, [await globalKeyboards.get_back_to_start_menu_kb_button()],
    False)


# Отправка сообщения с выбором какую информацию получить о предстоящем концерте
async def choose_future_concert_info(call: types.CallbackQuery, state: FSMContext) -> None:
    temp = call.data.split("|")

    future_concert_id = int(temp[1])

    future_concert = await AsyncORM.get_future_concert_artist_info_by_id(future_concert_id)

    if future_concert:
        data = await state.get_data()

        if "media_group_messages_ids" in data:
            for media_group_message_id in data["media_group_messages_ids"]:
                await bot.delete_message(call.from_user.id, media_group_message_id)
                await state.clear()

        await call.message.edit_text(userFutureConcertsTexts.show_future_concert_choose_info_text,
        reply_markup=await globalKeyboards.get_future_concert_info_kb(future_concert_id))
    else:
        await call.message.answer(globalTexts.data_notFound_text)


# Отправка сообщения с информацией о предстоящем концерте
async def show_future_concert_info(call: types.CallbackQuery, state: FSMContext) -> None:
    user_id = call.from_user.id
    message_id = call.message.message_id

    await bot.delete_message(user_id, message_id)

    temp = call.data.split("|")

    future_concert_id = int(temp[2])

    choosing_info = temp[3]
    
    if choosing_info == "artist":
        artist_info = await AsyncORM.get_future_concert_artist_info_by_id(future_concert_id)

        await mediaGroupSend(call, state, artist_info[1], artist_info[2])
        
        answer_message_text = userFutureConcertsTexts.show_future_concert_artist_info_withoutText_text

        if artist_info[0]:
            if not artist_info[1] and not artist_info[2]:
                answer_message_text = userFutureConcertsTexts.show_future_concert_artist_info_text.format(artist_info[0])
            else:
                answer_message_text = userFutureConcertsTexts.show_future_concert_artist_info_withImages_text.format(artist_info[0])

        await call.message.answer(answer_message_text,
        reply_markup=await globalKeyboards.back_to_future_concert_choose_kb(future_concert_id))

    elif choosing_info == "platform":
        platform_info = await AsyncORM.get_future_concert_platform_info_by_id(future_concert_id)

        await mediaGroupSend(call, state, platform_info[1], platform_info[2])

        answer_message_text = userFutureConcertsTexts.show_future_concert_platform_info_withoutText_text

        if platform_info[0]:
            if not platform_info[1] and not platform_info[2]:
                answer_message_text = userFutureConcertsTexts.show_future_concert_platform_info_text.format(platform_info[0])
            else:
                answer_message_text = userFutureConcertsTexts.show_future_concert_platform_info_withImages_text.format(platform_info[0])

        await call.message.answer(answer_message_text,
        reply_markup=await globalKeyboards.back_to_future_concert_choose_kb(future_concert_id))
    
    elif choosing_info == "price":
        ticket_price = await AsyncORM.get_future_concert_ticket_price_by_id(future_concert_id)

        await call.message.answer(userFutureConcertsTexts.show_future_concert_ticket_price_text.
        format(ticket_price), reply_markup=await globalKeyboards.back_to_future_concert_choose_kb(future_concert_id))


    elif choosing_info == "time":
        holding_time = await AsyncORM.get_future_concert_holding_time_by_id(future_concert_id)

        formatted_time = holding_time.strftime("%d.%m.%Y %H:%M")

        await call.message.answer(userFutureConcertsTexts.show_future_concert_holding_time_text.
        format(formatted_time), reply_markup=await globalKeyboards.back_to_future_concert_choose_kb(future_concert_id))
'''/Предстоящие концерты/'''



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

    '''Предстоящие концерты'''
    router.callback_query.register(send_future_concerts, lambda c: c.data == 'start|future_concerts')
    
    router.callback_query.register(choose_future_concert_info, lambda c: 
    re.match(r"^future_concerts\|(?P<future_concert_id>\d+)$", c.data))

    router.callback_query.register(show_future_concert_info, lambda c: 
    re.match(r"^start\|future_concerts\|(?P<future_concert_id>\d+)\|(artist|platform|price|time)$", c.data))
    '''/Предстоящие концерты/'''