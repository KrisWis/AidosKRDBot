from aiogram import types
from InstanceBot import router
from aiogram.filters import CommandStart, StateFilter
from utils import globalTexts, userPreviousConcertsTexts, userFutureConcertsTexts, userAboutUsTexts, userWhatsNewTexts, userDiscountsTexts
from keyboards import globalKeyboards
from database.orm import AsyncORM
from aiogram.fsm.context import FSMContext
import datetime
from InstanceBot import bot
from helpers import mediaGroupSend, sendPaginationMessage, deleteSendedMediaGroup, deleteMessage
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
    previous_concerts = await AsyncORM.get_all_previous_concerts()
    prefix = "previous_concerts"

    async def getPreviousConcertsButtonsAndAmount():
        previous_concerts = await AsyncORM.get_all_previous_concerts()

        buttons = [[types.InlineKeyboardButton(text=f"{previous_concert.name}",
        callback_data=f'{prefix}|{previous_concert.id}')] for previous_concert in previous_concerts]

        return [buttons, len(previous_concerts)]
    
    await sendPaginationMessage(call, state, previous_concerts, getPreviousConcertsButtonsAndAmount,
    prefix, userPreviousConcertsTexts.previous_concerts_text, 10, 
    [await globalKeyboards.get_back_to_start_menu_kb_button()],
    False)


# Отправка сообщения с информацией о прошедшем концерте
async def show_previous_concert(call: types.CallbackQuery, state: FSMContext) -> None:
    await deleteMessage(call)

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

    future_concerts = await AsyncORM.get_all_future_concerts()
    prefix = "future_concerts"

    async def getFutureConcertsButtonsAndAmount():
        future_concerts = await AsyncORM.get_all_future_concerts()

        buttons = [[types.InlineKeyboardButton(
        text=f"{future_concert.name if len(future_concert.name) <= 35 else future_concert.name[:35] + '...'} — {future_concert.holding_time.strftime("%d.%m.%Y %H:%M")}",
        callback_data=f'{prefix}|{future_concert.id}')] for future_concert in future_concerts]

        return [buttons, len(future_concerts)]
    
    await sendPaginationMessage(call, state, future_concerts, getFutureConcertsButtonsAndAmount,
    prefix, userFutureConcertsTexts.future_concerts_text, 10, 
    [await globalKeyboards.get_back_to_start_menu_kb_button()],
    False)


# Отправка сообщения с выбором какую информацию получить о предстоящем концерте
async def choose_future_concert_info(call: types.CallbackQuery, state: FSMContext) -> None:
    temp = call.data.split("|")

    future_concert_id = int(temp[1])

    future_concert = await AsyncORM.get_future_concert_artist_info_by_id(future_concert_id)

    if future_concert:
        await deleteSendedMediaGroup(state, call.from_user.id)

        await call.message.edit_text(userFutureConcertsTexts.show_future_concert_choose_info_text,
        reply_markup=await globalKeyboards.get_future_concert_info_kb(future_concert_id))
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
        reply_markup=await globalKeyboards.back_to_selection_menu_kb(f'future_concerts|{future_concert_id}'))

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
        reply_markup=await globalKeyboards.back_to_selection_menu_kb(f'future_concerts|{future_concert_id}'))
    
    elif choosing_info == "price":
        ticket_price = await AsyncORM.get_future_concert_ticket_price_by_id(future_concert_id)

        await call.message.answer(userFutureConcertsTexts.show_future_concert_ticket_price_text.
        format(ticket_price), reply_markup=await globalKeyboards.back_to_selection_menu_kb(f'future_concerts|{future_concert_id}'))


    elif choosing_info == "time":
        holding_time = await AsyncORM.get_future_concert_holding_time_by_id(future_concert_id)

        formatted_time = holding_time.strftime("%d.%m.%Y %H:%M")

        await call.message.answer(userFutureConcertsTexts.show_future_concert_holding_time_text.
        format(formatted_time), reply_markup=await globalKeyboards.back_to_selection_menu_kb(f'future_concerts|{future_concert_id}'))
'''/Предстоящие концерты/'''


'''О нас'''
# Отправка сообщения с выбором, что узнать о нас
async def send_about_us_choice(call: types.CallbackQuery) -> None:

    await call.message.edit_text(userAboutUsTexts.about_us_choice_text, reply_markup=await globalKeyboards.about_us_choice_kb())


# Отправка сообщения с информацией о нас
async def send_about_us_info(call: types.CallbackQuery) -> None:

    await call.message.edit_text(userAboutUsTexts.about_us_text, reply_markup=await globalKeyboards.back_to_selection_menu_kb('start|about_us'))


# Отправка сообщения с информацией о нас
async def send_about_organization_info(call: types.CallbackQuery) -> None:

    await call.message.edit_text(userAboutUsTexts.about_organization_text,
    reply_markup=await globalKeyboards.back_to_selection_menu_kb('start|about_us'))
'''/О нас/'''


'''Что нового?'''
# Отправка сообщения со меню выбора "Что нового?"
async def send_what_is_new_selection_menu(call: types.CallbackQuery, state: FSMContext) -> None:
    
    await deleteSendedMediaGroup(state, call.from_user.id)

    await call.message.edit_text(userWhatsNewTexts.what_is_new_choice_text,
    reply_markup=await globalKeyboards.what_is_new_selection_menu_kb())


'''Новости команды'''
# Отправка сообщения со всеми новостями команды
async def send_team_news(call: types.CallbackQuery, state: FSMContext) -> None:
    team_news = await AsyncORM.get_all_team_news()
    prefix = "team_news"

    async def getTeamNewsButtonsAndAmount():
        team_news = await AsyncORM.get_all_team_news()

        buttons = [[types.InlineKeyboardButton(
        text=team_news_item.name,
        callback_data=f'{prefix}|{team_news_item.id}')] for team_news_item in team_news]

        return [buttons, len(team_news)]
    
    await sendPaginationMessage(call, state, team_news, getTeamNewsButtonsAndAmount,
    prefix, userWhatsNewTexts.team_news_text, 10, 
    [await globalKeyboards.get_back_to_selection_menu_kb_button('start|what_is_new')], False)


# Отправка сообщения с информацией о новости
async def show_team_news_item(call: types.CallbackQuery, state: FSMContext) -> None:
    await deleteMessage(call)

    temp = call.data.split("|")

    team_news_item_id = int(temp[1])

    team_news_item = await AsyncORM.get_team_news_item_by_id(team_news_item_id)

    if team_news_item:
        await mediaGroupSend(call, state, team_news_item.photo_file_ids, team_news_item.video_file_ids)

        answer_message_text = userWhatsNewTexts.show_team_news_withoutText_text.format(team_news_item.name)

        if team_news_item.text:
            if not team_news_item.photo_file_ids and not team_news_item.video_file_ids:
                answer_message_text = userWhatsNewTexts.show_team_news_text.format(team_news_item.name, team_news_item.text)
            else:
                answer_message_text = userWhatsNewTexts.show_team_news_withImages_text.format(team_news_item.name, team_news_item.text)

        await call.message.answer(answer_message_text, 
        reply_markup=await globalKeyboards.back_to_selection_menu_kb('start|what_is_new|team_news'))
    else:
        await call.message.answer(globalTexts.data_notFound_text)
'''Новости команды'''


'''Эксклюзивные треки'''
# Отправка сообщения со всеми эксклюзивными треками
async def send_exclusive_tracks(call: types.CallbackQuery, state: FSMContext) -> None:
    exclusive_tracks = await AsyncORM.get_all_exclusive_tracks()
    prefix = "exclusive_tracks"

    async def getExclusiveTracksButtonsAndAmount():
        exclusive_tracks = await AsyncORM.get_all_exclusive_tracks()

        buttons = [[types.InlineKeyboardButton(
        text=exclusive_track.name,
        callback_data=f'{prefix}|{exclusive_track.id}')] for exclusive_track in exclusive_tracks]

        return [buttons, len(exclusive_tracks)]
    
    await sendPaginationMessage(call, state, exclusive_tracks, getExclusiveTracksButtonsAndAmount,
    prefix, userWhatsNewTexts.exclusive_from_concert_text, 10, 
    [await globalKeyboards.get_back_to_selection_menu_kb_button('start|what_is_new')], False)


# Отправка сообщения с эксклюзивным треком
async def show_exclusive_track(call: types.CallbackQuery) -> None:
    await deleteMessage(call)

    temp = call.data.split("|")

    exclusive_track_id = int(temp[1])

    exclusive_track = await AsyncORM.get_exclusive_track_by_id(exclusive_track_id)

    if exclusive_track:
        await call.message.answer_audio(audio=exclusive_track.audio_file_id,
        caption=exclusive_track.audio_file_info,
        reply_markup=await globalKeyboards.back_to_selection_menu_kb('start|what_is_new|exclusive_tracks'))
    else:
        await call.message.answer(globalTexts.data_notFound_text)
'''/Эксклюзивные треки/'''


'''Музыка с концерта'''
# Отправка сообщения со всей музыкой с концертов
async def send_concert_music(call: types.CallbackQuery, state: FSMContext) -> None:
    concert_music = await AsyncORM.get_all_concert_music()
    prefix = "concert_music"

    async def getConcertMusicButtonsAndAmount():
        concert_music = await AsyncORM.get_all_concert_music()

        buttons = [[types.InlineKeyboardButton(
        text=concert_music_item.name,
        callback_data=f'{prefix}|{concert_music_item.id}')] for concert_music_item in concert_music]

        return [buttons, len(concert_music)]
    
    await sendPaginationMessage(call, state, concert_music, getConcertMusicButtonsAndAmount,
    prefix, userWhatsNewTexts.concert_music_text, 10, 
    [await globalKeyboards.get_back_to_selection_menu_kb_button('start|what_is_new')], False)


# Отправка сообщения с музыкой с концерта
async def show_concert_music(call: types.CallbackQuery) -> None:
    await deleteMessage(call)

    temp = call.data.split("|")

    concert_music_item_id = int(temp[1])

    concert_music_item = await AsyncORM.get_concert_music_item_by_id(concert_music_item_id)

    if concert_music_item:
        await call.message.answer_audio(audio=concert_music_item.audio_file_id,
        caption=concert_music_item.audio_file_info,
        reply_markup=await globalKeyboards.back_to_selection_menu_kb('start|what_is_new|concert_music'))
    else:
        await call.message.answer(globalTexts.data_notFound_text)
'''/Музыка с концерта/'''
'''/Что нового?/'''


'''Скидки и акции'''
# Отправка сообщения с меню выбора "Скидки и акции"
async def send_discounts_selection_menu(call: types.CallbackQuery, state: FSMContext) -> None:
    
    await deleteSendedMediaGroup(state, call.from_user.id)

    await call.message.edit_text(userDiscountsTexts.discounts_choice_text,
    reply_markup=await globalKeyboards.discounts_selection_menu_kb())


'''Скидки'''
# Отправка сообщения со всеми акциями
async def send_rebates(call: types.CallbackQuery, state: FSMContext) -> None:
    rebates = await AsyncORM.get_all_rebates()
    prefix = "rebates"

    async def getRebatesButtonsAndAmount():
        rebates = await AsyncORM.get_all_rebates()

        buttons = [[types.InlineKeyboardButton(
        text=rebate.name,
        callback_data=f'{prefix}|{rebate.id}')] for rebate in rebates]

        return [buttons, len(rebates)]
    
    await sendPaginationMessage(call, state, rebates, getRebatesButtonsAndAmount,
    prefix, userDiscountsTexts.rebates_text, 10,
    [await globalKeyboards.get_back_to_selection_menu_kb_button('start|discounts')], False)


# Отправка сообщения с информацией о скидке
async def show_rebate(call: types.CallbackQuery, state: FSMContext) -> None:
    await deleteMessage(call)

    temp = call.data.split("|")

    rebate_id = int(temp[1])

    rebate = await AsyncORM.get_rebate_by_id(rebate_id)

    if rebate:
        await mediaGroupSend(call, state, rebate.photo_file_ids, rebate.video_file_ids)

        answer_message_text = userDiscountsTexts.show_rebates_withoutText_text.format(rebate.name)

        if rebate.text:
            if not rebate.photo_file_ids and not rebate.video_file_ids:
                answer_message_text = userDiscountsTexts.show_rebates_text.format(rebate.name, rebate.text)
            else:
                answer_message_text = userDiscountsTexts.show_rebates_withImages_text.format(rebate.name, rebate.text)

        await call.message.answer(answer_message_text,
        reply_markup=await globalKeyboards.back_to_selection_menu_kb('start|discounts|rebates'))
    else:
        await call.message.answer(globalTexts.data_notFound_text)
'''/Скидки/'''


'''Акции'''
# Отправка сообщения со всеми акциями
async def send_stocks(call: types.CallbackQuery, state: FSMContext) -> None:
    stocks = await AsyncORM.get_all_stocks()
    prefix = "stocks"

    async def getStocksButtonsAndAmount():
        stocks = await AsyncORM.get_all_stocks()

        buttons = [[types.InlineKeyboardButton(
        text=stock.name,
        callback_data=f'{prefix}|{stock.id}')] for stock in stocks]

        return [buttons, len(stocks)]
    
    await sendPaginationMessage(call, state, stocks, getStocksButtonsAndAmount,
    prefix, userDiscountsTexts.stocks_text, 10, 
    [await globalKeyboards.get_back_to_selection_menu_kb_button('start|discounts')], False)


# Отправка сообщения с информацией об акции
async def show_stock(call: types.CallbackQuery, state: FSMContext) -> None:
    await deleteMessage(call)

    temp = call.data.split("|")

    stock_id = int(temp[1])

    stock = await AsyncORM.get_stock_by_id(stock_id)

    if stock:
        await mediaGroupSend(call, state, stock.photo_file_ids, stock.video_file_ids)

        answer_message_text = userDiscountsTexts.show_stocks_withoutText_text.format(stock.name)

        if stock.text:
            if not stock.photo_file_ids and not stock.video_file_ids:
                answer_message_text = userDiscountsTexts.show_stocks_text.format(stock.name, stock.text)
            else:
                answer_message_text = userDiscountsTexts.show_stocks_withImages_text.format(stock.name, stock.text)

        await call.message.answer(answer_message_text,
        reply_markup=await globalKeyboards.back_to_selection_menu_kb('start|discounts|stocks'))
    else:
        await call.message.answer(globalTexts.data_notFound_text)
'''/Акции/'''
'''/Скидки и акции/'''


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

    '''О нас'''
    router.callback_query.register(send_about_us_choice, lambda c: c.data == 'start|about_us')

    router.callback_query.register(send_about_us_info, lambda c: c.data == 'start|about_us|about_us')

    router.callback_query.register(send_about_organization_info, lambda c: c.data == 'start|about_us|about_organization')
    '''/О нас/'''

    '''Что нового?'''
    router.callback_query.register(send_what_is_new_selection_menu, lambda c: c.data == 'start|what_is_new')

    '''Новости команды'''
    router.callback_query.register(send_team_news, lambda c: c.data == 'start|what_is_new|team_news')
    
    router.callback_query.register(show_team_news_item, lambda c: 
    re.match(r"^team_news\|(?P<team_news_item_id>\d+)$", c.data))
    '''/Новости команды/'''

    '''Эксклюзивные треки'''
    router.callback_query.register(send_exclusive_tracks, lambda c: c.data == 'start|what_is_new|exclusive_tracks')

    router.callback_query.register(show_exclusive_track, lambda c: 
    re.match(r"^exclusive_tracks\|(?P<exclusive_track_id>\d+)$", c.data))
    '''/Эксклюзивные треки/'''

    '''Музыка с концерта'''
    router.callback_query.register(send_concert_music, lambda c: c.data == 'start|what_is_new|concert_music')

    router.callback_query.register(show_concert_music, lambda c: 
    re.match(r"^concert_music\|(?P<concert_music_item_id>\d+)$", c.data))
    '''/Музыка с концерта/'''
    '''/Что нового?/'''

    '''Скидки и акции'''
    router.callback_query.register(send_discounts_selection_menu, lambda c: c.data == 'start|discounts')

    '''Скидки'''
    router.callback_query.register(send_rebates, lambda c: c.data == 'start|discounts|rebates')
    
    router.callback_query.register(show_rebate, lambda c: 
    re.match(r"^rebates\|(?P<rebate_id>\d+)$", c.data))
    '''/Скидки/'''

    '''Акции'''
    router.callback_query.register(send_stocks, lambda c: c.data == 'start|discounts|stocks')

    router.callback_query.register(show_stock, lambda c: 
    re.match(r"^stocks\|(?P<stock_id>\d+)$", c.data))
    '''/Акции/'''
    '''/Скидки и акции/'''