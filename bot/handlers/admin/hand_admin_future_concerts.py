from aiogram import types
from InstanceBot import router, bot
from utils import adminFutureConcertsTexts, globalTexts, userFutureConcertsTexts
from keyboards import adminKeyboards
from aiogram.fsm.context import FSMContext
from database.orm import AsyncORM
from states.Admin import FutureConcertsStates
from aiogram.filters import StateFilter
import datetime
from helpers import albumInfoProcess, mediaGroupSend, sendPaginationMessage, futureConcertChangeInfo, deleteMessage
from RunBot import logger
import re


'''Предстоящие концерты'''
# Отправка сообщения со всеми прошедшими концертами
async def send_future_concerts(call: types.CallbackQuery, state: FSMContext) -> None:
    future_concerts = await AsyncORM.get_all_future_concerts()
    prefix = "admin_future_concerts"

    async def getFutureConcertsButtonsAndAmount():
        future_concerts = await AsyncORM.get_all_future_concerts()

        buttons = [[types.InlineKeyboardButton(
        text=f"{future_concert.name if len(future_concert.name) <= 35 else future_concert.name[:35] + '...'} — {future_concert.holding_time.strftime("%d.%m.%Y %H:%M")}",
        callback_data=f'{prefix}|{future_concert.id}')] for future_concert in future_concerts]

        return [buttons, len(future_concerts)]
    
    await sendPaginationMessage(call, state, future_concerts, getFutureConcertsButtonsAndAmount,
    prefix, adminFutureConcertsTexts.future_concerts_text, 10, [await adminKeyboards.get_kb_addButton('future_concerts'), 
    await adminKeyboards.get_back_to_admin_menu_kb_button()])
    

# Отправка сообщения о том, чтобы администратор прислал название предстоящего концерта
async def wait_future_concert_name(call: types.CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(adminFutureConcertsTexts.wait_future_concert_name_text)

    await state.set_state(FutureConcertsStates.wait_name)


# Ожидание названия предстоящего концерта. Отправка сообщения о том, чтобы администратор прислал информацию о артисте предстоящего концерта
async def wait_future_concert_artist_info(message: types.Message, state: FSMContext):
    future_concert_name = message.text

    if future_concert_name:
        future_concert = await AsyncORM.get_future_concert_by_name(future_concert_name)

        if not future_concert:
            await state.update_data(future_concert_name=future_concert_name)

            await message.answer(adminFutureConcertsTexts.wait_future_concert_artist_info_text)

            await state.set_state(FutureConcertsStates.wait_artist_info)

        else:
            await message.answer(globalTexts.adding_data_error_text)
    else:
        await message.answer(globalTexts.data_isInvalid_text)


# Ожидание информации об артисте предстоящего концерта. Отправка сообщения о том, чтобы администратор прислал информацию о площадке предстоящего концерта
async def wait_future_concert_platform_info(message: types.Message, album: list[types.Message] = [], state: FSMContext = None):
    result = await albumInfoProcess(FutureConcertsStates.wait_artist_info, state, message, album)

    if not result:
        return
    
    user_text = result[0]
    photo_file_ids = result[1]
    video_file_ids = result[2]

    async def changeArtistInfo(future_concert_replace_id: int):
        await AsyncORM.change_futureConcert_artist_info(future_concert_replace_id, user_text,
        photo_file_ids, video_file_ids)

    data = await state.get_data()

    result = await futureConcertChangeInfo(data, state, message, changeArtistInfo, 
    adminFutureConcertsTexts.change_future_concert_artist_info_success_text)

    if not result:

        await state.update_data(future_concert_artist_info_text=user_text)
        await state.update_data(future_concert_artist_info_photo_file_ids=photo_file_ids)
        await state.update_data(future_concert_artist_info_video_file_ids=video_file_ids)

        await message.answer(adminFutureConcertsTexts.wait_future_concert_platform_info_text)

        await state.set_state(FutureConcertsStates.wait_platform_info)


# Ожидание информации о площадке предстоящего концерта. Отправка сообщения о том, чтобы администратор прислал время проведения предстоящего концерта
async def wait_future_concert_holding_time(message: types.Message, album: list[types.Message] = [], state: FSMContext = None):
    result = await albumInfoProcess(FutureConcertsStates.wait_platform_info, state, message, album)

    if not result:
        return
    
    user_text = result[0]
    photo_file_ids = result[1]
    video_file_ids = result[2]

    async def changePlatformInfo(future_concert_replace_id: int):
        await AsyncORM.change_futureConcert_platform_info(future_concert_replace_id,
        user_text, photo_file_ids, video_file_ids)

    data = await state.get_data()

    result = await futureConcertChangeInfo(data, state, message, changePlatformInfo, 
    adminFutureConcertsTexts.change_future_concert_platform_info_success_text)

    if not result:
        await state.update_data(future_concert_platform_info_text=user_text)
        await state.update_data(future_concert_platform_info_photo_file_ids=photo_file_ids)
        await state.update_data(future_concert_platform_info_video_file_ids=video_file_ids)

        await message.answer(adminFutureConcertsTexts.wait_future_concert_holding_time_text)

        await state.set_state(FutureConcertsStates.wait_holding_time)


# Ожидание информации о времени проведения предстоящего концерта. Отправка сообщения о том, чтобы администратор прислал стоимость билета предстоящего концерта
async def wait_future_concert_ticket_price(message: types.Message, state: FSMContext) -> None:
    future_concert_holding_time = message.text

    try:
        if re.match(r'^\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}$', future_concert_holding_time):

            future_concert_holding_time = datetime.datetime.strptime(future_concert_holding_time, '%d.%m.%Y %H:%M')
            now = datetime.datetime.now()

            if now >= future_concert_holding_time:
                await message.answer(globalTexts.date_inPastIsInvalid_text)
                return
            
            async def changeHoldingTime(future_concert_replace_id: int):
                await AsyncORM.change_futureConcert_holding_time(future_concert_replace_id, future_concert_holding_time)

            data = await state.get_data()

            result = await futureConcertChangeInfo(data, state, message, changeHoldingTime, 
            adminFutureConcertsTexts.change_future_concert_holding_time_success_text)

            if not result:
                await state.update_data(future_concert_holding_time=future_concert_holding_time)
                
                await message.answer(adminFutureConcertsTexts.wait_future_concert_ticket_price_text)

                await state.set_state(FutureConcertsStates.wait_ticket_price)

            return

    except Exception as e:
        logger.info(e)

    await message.answer(globalTexts.data_isInvalid_text)


# Ожидание информации о стоимости билета предстоящего концерта. Добавление предстоящего концерта в базу данных.
async def add_future_concert(message: types.Message, state: FSMContext) -> None:
    future_concert_ticket_price = message.text

    if future_concert_ticket_price.isdigit():
        future_concert_ticket_price = int(future_concert_ticket_price)
        
        async def changeTicketPrice(future_concert_replace_id: int):
            await AsyncORM.change_futureConcert_ticket_price(future_concert_replace_id, future_concert_ticket_price)

        data = await state.get_data()
        
        result = await futureConcertChangeInfo(data, state, message, changeTicketPrice, 
        adminFutureConcertsTexts.change_future_concert_ticket_price_success_text)

        if not result:
            
            now = datetime.datetime.now()

            try:
                data = await state.get_data()
                await AsyncORM.add_future_concert(data["future_concert_name"], now, data["future_concert_artist_info_text"], 
                data["future_concert_platform_info_text"], data["future_concert_holding_time"], future_concert_ticket_price,
                data["future_concert_artist_info_photo_file_ids"], data["future_concert_artist_info_video_file_ids"],
                data["future_concert_platform_info_photo_file_ids"], data["future_concert_platform_info_video_file_ids"])

                await message.answer(adminFutureConcertsTexts.add_future_concert_success_text, reply_markup=await adminKeyboards.back_to_admin_menu_kb())

                await state.clear()
            except Exception as e:
                logger.info(e)
                await message.answer(globalTexts.adding_data_error_text)

    else:
        await message.answer(globalTexts.data_isInvalid_text)


# Отправка сообщения с выбором какую информацию получить о предстоящем концерте
async def choose_future_concert_info(call: types.CallbackQuery) -> None:
    temp = call.data.split("|")

    future_concert_id = int(temp[1])

    future_concert = await AsyncORM.get_future_concert_artist_info_by_id(future_concert_id)

    if future_concert:
        await call.message.edit_text(adminFutureConcertsTexts.show_future_concert_choose_info_text,
        reply_markup=await adminKeyboards.get_future_concert_info_kb(future_concert_id))
    else:
        await call.message.answer(globalTexts.data_notFound_text)


# Отправка сообщения с информацией о предстоящем концерте
async def show_future_concert_info(call: types.CallbackQuery, state: FSMContext) -> None:
    await deleteMessage(call)

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
        reply_markup=await adminKeyboards.future_concert_actions_kb(future_concert_id, choosing_info))

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
        reply_markup=await adminKeyboards.future_concert_actions_kb(future_concert_id, choosing_info))
    
    elif choosing_info == "price":
        ticket_price = await AsyncORM.get_future_concert_ticket_price_by_id(future_concert_id)

        await call.message.answer(userFutureConcertsTexts.show_future_concert_ticket_price_text.format(ticket_price),
        reply_markup=await adminKeyboards.future_concert_actions_kb(future_concert_id, choosing_info))


    elif choosing_info == "time":
        holding_time = await AsyncORM.get_future_concert_holding_time_by_id(future_concert_id)

        formatted_time = holding_time.strftime("%d.%m.%Y %H:%M")

        await call.message.answer(userFutureConcertsTexts.show_future_concert_holding_time_text.format(formatted_time),
        reply_markup=await adminKeyboards.future_concert_actions_kb(future_concert_id, choosing_info))


# Подтверждение удаления информации о предстоящем концерте
async def confirm_delete_future_concert(call: types.CallbackQuery) -> None:

    temp = call.data.split("|")

    future_concert_id = int(temp[1])

    future_concert = await AsyncORM.get_future_concert_by_id(future_concert_id)

    if not future_concert:
        await call.message.edit_text(globalTexts.data_notFound_text)
        return

    await call.message.edit_text(adminFutureConcertsTexts.future_concert_actions_delete_confirmation_text.
    format(future_concert.name),
    reply_markup=await adminKeyboards.delete_confirmation_kb(future_concert.id, 'future_concerts'))


# Обработка подтверждения/отклонения удаления информации о предстоящем концерте
async def future_concert_delete_confirmation(call: types.CallbackQuery) -> None:

    temp = call.data.split("|")

    future_concert_id = int(temp[1])

    action = temp[3]

    future_concert = await AsyncORM.get_future_concert_by_id(future_concert_id)

    if not future_concert:
        await call.message.edit_text(globalTexts.data_notFound_text)
        return
    
    if action == "yes":
        await AsyncORM.delete_future_concert(future_concert_id)

        await call.message.edit_text(adminFutureConcertsTexts.future_concert_actions_delete_confirmation_yes_text.
        format(future_concert.name), reply_markup=await adminKeyboards.back_to_selection_menu_kb('future_concerts'))

    elif action == "no":
        await call.message.edit_text(adminFutureConcertsTexts.future_concert_actions_delete_confirmation_no_text.
        format(future_concert.name), reply_markup=await adminKeyboards.back_to_selection_menu_kb('future_concerts'))


# Отправка сообщения с тем, чтобы пользователь прислал обновлённую информацию для замены конкретной информации предстоящего концерта
async def replace_future_concert_info(call: types.CallbackQuery, state: FSMContext) -> None:
    temp = call.data.split("|")

    future_concert_id = int(temp[2])

    choosing_info = temp[4]

    await state.update_data(future_concert_replace_id=future_concert_id)
    
    if choosing_info == "artist":
        await call.message.edit_text(adminFutureConcertsTexts.edit_future_concert_artist_info_text)

        await state.set_state(FutureConcertsStates.wait_artist_info)

    elif choosing_info == "platform":
        await call.message.edit_text(adminFutureConcertsTexts.edit_future_concert_platform_info_text)

        await state.set_state(FutureConcertsStates.wait_platform_info)

    elif choosing_info == "time":
        await call.message.edit_text(adminFutureConcertsTexts.edit_future_concert_holding_time_text)

        await state.set_state(FutureConcertsStates.wait_holding_time)

    elif choosing_info == "price":
        await call.message.edit_text(adminFutureConcertsTexts.edit_future_concert_ticket_price_text)

        await state.set_state(FutureConcertsStates.wait_ticket_price)
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
    
    router.callback_query.register(choose_future_concert_info, lambda c: 
    re.match(r"^admin_future_concerts\|(?P<future_concert_id>\d+)$", c.data))

    router.callback_query.register(show_future_concert_info, lambda c: 
    re.match(r"^admin\|future_concerts\|(?P<future_concert_id>\d+)\|(artist|platform|price|time)$", c.data))

    router.callback_query.register(confirm_delete_future_concert, lambda c: 
    re.match(r"^future_concerts\|(\d+)\|delete$", c.data))

    router.callback_query.register(future_concert_delete_confirmation, lambda c: 
    re.match(r"^future_concerts\|(?P<future_concert_id>\d+)\|delete\|(?P<choice>yes|no)$", c.data))

    router.callback_query.register(replace_future_concert_info, lambda c: 
    re.match(r"^admin\|future_concerts\|(\d+)\|replace\|(artist|platform|price|time)$", c.data))
    '''/Предстоящие концерты/'''