from aiogram import types
from InstanceBot import router
from aiogram.fsm.context import FSMContext
from utils import userWhatsNewTexts, adminWhatIsNewTexts, globalTexts
from keyboards import adminKeyboards
from database.orm import AsyncORM
from helpers import sendPaginationMessage, mediaGroupSend, albumInfoProcess, deleteSendedMediaGroup, deleteMessage
from states.Admin import WhatIsNewStates
from RunBot import logger
import datetime
from aiogram.filters import StateFilter
import re


'''Что нового?'''
# Отправка сообщения с меню выбора "Что нового?"
async def send_what_is_new_selection_menu(call: types.CallbackQuery, state: FSMContext) -> None:
    
    await deleteSendedMediaGroup(state, call.from_user.id)

    await call.message.edit_text(userWhatsNewTexts.what_is_new_choice_text,
    reply_markup=await adminKeyboards.what_is_new_selection_menu_kb())


'''Новости команды'''
# Отправка сообщения со всеми новостями команды
async def send_team_news(call: types.CallbackQuery, state: FSMContext) -> None:
    team_news = await AsyncORM.get_all_team_news()
    prefix = "admin_team_news"

    async def getTeamNewsButtonsAndAmount():
        team_news = await AsyncORM.get_all_team_news()

        buttons = [[types.InlineKeyboardButton(
        text=team_news_item.name,
        callback_data=f'{prefix}|{team_news_item.id}')] for team_news_item in team_news]

        return [buttons, len(team_news)]
    
    await sendPaginationMessage(call, state, team_news, getTeamNewsButtonsAndAmount,
    prefix, userWhatsNewTexts.team_news_text, 10, [await adminKeyboards.get_kb_addButton('team_news'), 
    await adminKeyboards.get_kb_backToSelectionMenuButton('admin|what_is_new')])


# Отправка сообщения о том, чтобы администратор прислал название новости
async def wait_team_news_item_name(call: types.CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(adminWhatIsNewTexts.wait_team_news_item_name_text)

    await state.set_state(WhatIsNewStates.team_news_item_wait_name)


# Ожидание названия новости команды. Отправка сообщения о том, чтобы администратор прислал информацию о новости
async def wait_team_news_item_info(message: types.Message, state: FSMContext):
    team_news_item_name = message.text

    if team_news_item_name:
        team_news_item = await AsyncORM.get_team_news_item_by_name(team_news_item_name)

        if not team_news_item:
            await state.update_data(team_news_item_name=team_news_item_name)

            await message.answer(adminWhatIsNewTexts.wait_team_news_item_info_text)

            await state.set_state(WhatIsNewStates.team_news_item_wait_info)

        else:
            await message.answer(globalTexts.adding_data_error_text)
    else:
        await message.answer(globalTexts.data_isInvalid_text)


# Ожидание информации новости команды. Добавление новости в базу данных
async def add_team_news_item(message: types.Message, album: list[types.Message] = [], state: FSMContext = None):
    result = await albumInfoProcess(WhatIsNewStates.team_news_item_wait_info, state, message, album)

    if not result:
        await message.answer(globalTexts.data_isInvalid_text)
        return

    user_text = result[0]
    photo_file_ids = result[1]
    video_file_ids = result[2]
    now = datetime.datetime.now()
    data = await state.get_data()

    if "team_news_item_replace_id" in data:
        team_news_item_replace_id = int(data["team_news_item_replace_id"])

        await AsyncORM.change_team_news_item_info(team_news_item_replace_id,
        user_text, photo_file_ids, video_file_ids)

        team_news_item = await AsyncORM.get_team_news_item_by_id(team_news_item_replace_id)

        await message.answer(adminWhatIsNewTexts.change_team_news_item_success_text
        .format(team_news_item.name), reply_markup=await adminKeyboards.back_to_admin_menu_kb())
    else:
        try:
            await AsyncORM.add_team_news_item(data["team_news_item_name"], now, user_text, photo_file_ids, video_file_ids)

            await message.answer(adminWhatIsNewTexts.add_team_news_item_success_text,
            reply_markup=await adminKeyboards.back_to_admin_menu_kb())
        except Exception as e:
            logger.info(e)
            await message.answer(globalTexts.adding_data_error_text)

    await state.clear()


# Отправка сообщения с информацией о новости и возможностью удаления/изменения информации
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
        reply_markup=await adminKeyboards.actions_kb(team_news_item.id, 'team_news'))
    else:
        await call.message.answer(globalTexts.data_notFound_text)


# Обработка изменения/удаления информации о новости команды
async def team_news_item_actions(call: types.CallbackQuery, state: FSMContext) -> None:

    temp = call.data.split("|")

    team_news_item_id = int(temp[1])

    action = temp[2]

    team_news_item = await AsyncORM.get_team_news_item_by_id(team_news_item_id)

    if not team_news_item:
        await call.message.answer(globalTexts.data_notFound_text)
        return
    
    if action == "replace":
        await call.message.edit_text(adminWhatIsNewTexts.team_news_item_actions_edit_text)
        await state.update_data(team_news_item_replace_id=team_news_item_id)

        await state.set_state(WhatIsNewStates.team_news_item_wait_info)

    elif action == "delete":
        await call.message.edit_text(adminWhatIsNewTexts.team_news_item_actions_delete_confirmation_text.
        format(team_news_item.name),
        reply_markup=await adminKeyboards.delete_confirmation_kb(team_news_item.id, 'team_news'))


# Обработка подтверждения/отклонения удаления информации о новости команды
async def team_news_item_delete_confirmation(call: types.CallbackQuery) -> None:

    temp = call.data.split("|")

    team_news_item_id = int(temp[1])

    action = temp[3]

    team_news_item = await AsyncORM.get_team_news_item_by_id(team_news_item_id)

    if not team_news_item:
        await call.message.answer(globalTexts.data_notFound_text)
        return
    
    if action == "yes":
        await AsyncORM.delete_team_news_item(team_news_item_id)

        await call.message.edit_text(adminWhatIsNewTexts.team_news_item_actions_delete_confirmation_yes_text.
        format(team_news_item.name), reply_markup=await adminKeyboards.back_to_selection_menu_kb('what_is_new'))

    elif action == "no":
        await call.message.edit_text(adminWhatIsNewTexts.team_news_item_actions_delete_confirmation_no_text.
        format(team_news_item.name), reply_markup=await adminKeyboards.back_to_selection_menu_kb('what_is_new'))
'''/Новости команды/'''


'''Эксклюзивные треки'''
# Отправка сообщения со всеми эксклюзивными треками
async def send_exclusive_tracks(call: types.CallbackQuery, state: FSMContext) -> None:
    exclusive_tracks = await AsyncORM.get_all_exclusive_tracks()
    prefix = "admin_exclusive_tracks"

    async def getExclusiveTracksButtonsAndAmount():
        exclusive_tracks = await AsyncORM.get_all_exclusive_tracks()

        buttons = [[types.InlineKeyboardButton(
        text=exclusive_track.name,
        callback_data=f'{prefix}|{exclusive_track.id}')] for exclusive_track in exclusive_tracks]

        return [buttons, len(exclusive_tracks)]
    
    await sendPaginationMessage(call, state, exclusive_tracks, getExclusiveTracksButtonsAndAmount,
    prefix, adminWhatIsNewTexts.exclusive_tracks_text, 10, 
    [await adminKeyboards.get_kb_addButton('exclusive_tracks'), 
    await adminKeyboards.get_kb_backToSelectionMenuButton('admin|what_is_new')])


# Отправка сообщения о том, чтобы администратор прислал название эксклюзивного трека
async def wait_exclusive_track_name(call: types.CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(adminWhatIsNewTexts.wait_exclusive_track_name_text)

    await state.set_state(WhatIsNewStates.exclusive_track_wait_name)


# Ожидание названия эксклюзивного трека. Отправка сообщения о том, чтобы администратор прислал эксклюзивный трек/информацию о нём
async def wait_exclusive_track(message: types.Message, state: FSMContext):
    exclusive_track_name = message.text

    if exclusive_track_name:
        exclusive_track = await AsyncORM.get_exclusive_track_by_name(exclusive_track_name)

        if not exclusive_track:
            await state.update_data(exclusive_track_name=exclusive_track_name)

            await message.answer(adminWhatIsNewTexts.wait_exclusive_track_info_text)

            await state.set_state(WhatIsNewStates.exclusive_track_wait_info)

        else:
            await message.answer(globalTexts.adding_data_error_text)
    else:
        await message.answer(globalTexts.data_isInvalid_text)


# Ожидание эксклюзивного трека. Добавление эксклюзивного трека в базу данных
async def add_exclusive_track(message: types.Message, state: FSMContext):
    audio_file = message.audio
    audio_file_info = message.caption or ""

    if not audio_file:
        await message.answer(globalTexts.data_isInvalid_text)
        return

    now = datetime.datetime.now()
    data = await state.get_data()

    if "exclusive_track_replace_id" in data:
        exclusive_track_replace_id = int(data["exclusive_track_replace_id"])

        await AsyncORM.change_exclusive_track(exclusive_track_replace_id, audio_file.file_id,
        audio_file_info)

        exclusive_track = await AsyncORM.get_exclusive_track_by_id(exclusive_track_replace_id)

        await message.answer(adminWhatIsNewTexts.change_exclusive_track_success_text
        .format(exclusive_track.name), reply_markup=await adminKeyboards.back_to_admin_menu_kb())
    else:
        try:
            await AsyncORM.add_exclusive_track(data["exclusive_track_name"], now,
            audio_file.file_id, audio_file_info)

            await message.answer(adminWhatIsNewTexts.add_exclusive_track_success_text,
            reply_markup=await adminKeyboards.back_to_admin_menu_kb())
        except Exception as e:
            logger.info(e)
            await message.answer(globalTexts.adding_data_error_text)

    await state.clear()


# Отправка сообщения с эксклюзивным треком и возможностью удаления/изменения информации
async def show_exclusive_track(call: types.CallbackQuery) -> None:
    await deleteMessage(call)

    temp = call.data.split("|")

    exclusive_track_id = int(temp[1])

    exclusive_track = await AsyncORM.get_exclusive_track_by_id(exclusive_track_id)

    if exclusive_track:
        await call.message.answer_audio(audio=exclusive_track.audio_file_id,
        caption=exclusive_track.audio_file_info,
        reply_markup=await adminKeyboards.actions_kb(exclusive_track.id, 'exclusive_tracks'))
    else:
        await call.message.answer(globalTexts.data_notFound_text)


# Обработка изменения/удаления информации об эксклюзивном треке
async def exclusive_track_actions(call: types.CallbackQuery, state: FSMContext) -> None:

    temp = call.data.split("|")

    exclusive_track_id = int(temp[1])

    action = temp[2]

    exclusive_track = await AsyncORM.get_exclusive_track_by_id(exclusive_track_id)

    if not exclusive_track:
        await call.message.answer(globalTexts.data_notFound_text)
        return
    
    await deleteMessage(call)
    
    if action == "replace":
        await call.message.answer(adminWhatIsNewTexts.exclusive_track_actions_edit_text)
        await state.update_data(exclusive_track_replace_id=exclusive_track_id)

        await state.set_state(WhatIsNewStates.exclusive_track_wait_info)

    elif action == "delete":
        await call.message.answer(adminWhatIsNewTexts.exclusive_track_actions_delete_confirmation_text.
        format(exclusive_track.name),
        reply_markup=await adminKeyboards.delete_confirmation_kb(exclusive_track.id, 'exclusive_tracks'))


# Обработка подтверждения/отклонения удаления информации об эксклюзивном треке
async def exclusive_track_delete_confirmation(call: types.CallbackQuery) -> None:

    temp = call.data.split("|")

    exclusive_track_id = int(temp[1])

    action = temp[3]

    exclusive_track = await AsyncORM.get_exclusive_track_by_id(exclusive_track_id)

    if not exclusive_track:
        await call.message.answer(globalTexts.data_notFound_text)
        return
    
    if action == "yes":
        await AsyncORM.delete_exclusive_track(exclusive_track_id)

        await call.message.edit_text(adminWhatIsNewTexts.exclusive_track_actions_delete_confirmation_yes_text.
        format(exclusive_track.name), reply_markup=await adminKeyboards.back_to_selection_menu_kb('what_is_new'))

    elif action == "no":
        await call.message.edit_text(adminWhatIsNewTexts.team_news_item_actions_delete_confirmation_no_text.
        format(exclusive_track.name), reply_markup=await adminKeyboards.back_to_selection_menu_kb('what_is_new'))
'''/Эксклюзивные треки/'''


'''Музыка с концерта'''
# Отправка сообщения со всей музыкой с концерта
async def send_concert_music(call: types.CallbackQuery, state: FSMContext) -> None:
    concert_music = await AsyncORM.get_all_concert_music()
    prefix = "admin_concert_music"

    async def getConcertMusicButtonsAndAmount():
        concert_music = await AsyncORM.get_all_concert_music()

        buttons = [[types.InlineKeyboardButton(
        text=concert_music_item.name,
        callback_data=f'{prefix}|{concert_music_item.id}')] for concert_music_item in concert_music]

        return [buttons, len(concert_music)]
    
    await sendPaginationMessage(call, state, concert_music, getConcertMusicButtonsAndAmount,
    prefix, adminWhatIsNewTexts.concert_music_text, 10, 
    [await adminKeyboards.get_kb_addButton('concert_music'), 
    await adminKeyboards.get_kb_backToSelectionMenuButton('admin|what_is_new')])


# Отправка сообщения о том, чтобы администратор прислал название музыки с концерта
async def wait_concert_music_item_name(call: types.CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(adminWhatIsNewTexts.wait_concert_music_item_name_text)

    await state.set_state(WhatIsNewStates.concert_music_item_wait_name)


# Ожидание названия музыки с концерта. Отправка сообщения о том, чтобы администратор прислал музыку с концерта/информацию о нём
async def wait_concert_music_item(message: types.Message, state: FSMContext):
    concert_music_item_name = message.text

    if concert_music_item_name:
        concert_music_item = await AsyncORM.get_concert_music_item_by_name(concert_music_item_name)

        if not concert_music_item:
            await state.update_data(concert_music_item_name=concert_music_item_name)

            await message.answer(adminWhatIsNewTexts.wait_concert_music_item_info_text)

            await state.set_state(WhatIsNewStates.concert_music_item_wait_info)

        else:
            await message.answer(globalTexts.adding_data_error_text)
    else:
        await message.answer(globalTexts.data_isInvalid_text)


# Ожидание музыки с концерта. Добавление музыки с концерта в базу данных
async def add_concert_music_item(message: types.Message, state: FSMContext):
    audio_file = message.audio
    audio_file_info = message.caption or ""

    if not audio_file:
        await message.answer(globalTexts.data_isInvalid_text)
        return

    now = datetime.datetime.now()
    data = await state.get_data()

    if "concert_music_item_replace_id" in data:
        concert_music_item_replace_id = int(data["concert_music_item_replace_id"])

        await AsyncORM.change_concert_music_item(concert_music_item_replace_id, audio_file.file_id,
        audio_file_info)

        concert_music_item = await AsyncORM.get_concert_music_item_by_id(concert_music_item_replace_id)

        await message.answer(adminWhatIsNewTexts.change_concert_music_item_success_text
        .format(concert_music_item.name), reply_markup=await adminKeyboards.back_to_admin_menu_kb())
    else:
        try:
            await AsyncORM.add_concert_music_item(data["concert_music_item_name"], now,
            audio_file.file_id, audio_file_info)

            await message.answer(adminWhatIsNewTexts.add_concert_music_item_success_text,
            reply_markup=await adminKeyboards.back_to_admin_menu_kb())
        except Exception as e:
            logger.info(e)
            await message.answer(globalTexts.adding_data_error_text)

    await state.clear()


# Отправка сообщения с музыкой с концерта и возможностью удаления/изменения информации
async def show_concert_music_item(call: types.CallbackQuery) -> None:
    await deleteMessage(call)

    temp = call.data.split("|")

    concert_music_item_id = int(temp[1])

    concert_music_item = await AsyncORM.get_concert_music_item_by_id(concert_music_item_id)

    if concert_music_item:
        await call.message.answer_audio(audio=concert_music_item.audio_file_id,
        caption=concert_music_item.audio_file_info,
        reply_markup=await adminKeyboards.actions_kb(concert_music_item.id, 'concert_music'))
    else:
        await call.message.answer(globalTexts.data_notFound_text)


# Обработка изменения/удаления информации о музыке с концерта
async def concert_music_item_actions(call: types.CallbackQuery, state: FSMContext) -> None:

    temp = call.data.split("|")

    concert_music_item_id = int(temp[1])

    action = temp[2]

    concert_music_item = await AsyncORM.get_concert_music_item_by_id(concert_music_item_id)

    if not concert_music_item:
        await call.message.answer(globalTexts.data_notFound_text)
        return
    
    await deleteMessage(call)
    
    if action == "replace":
        await call.message.answer(adminWhatIsNewTexts.concert_music_item_actions_edit_text)
        await state.update_data(concert_music_item_replace_id=concert_music_item_id)

        await state.set_state(WhatIsNewStates.concert_music_item_wait_info)

    elif action == "delete":
        await call.message.answer(adminWhatIsNewTexts.concert_music_item_actions_delete_confirmation_text.
        format(concert_music_item.name),
        reply_markup=await adminKeyboards.delete_confirmation_kb(concert_music_item.id, 'concert_music'))


# Обработка подтверждения/отклонения удаления информации о музыке с концерта
async def concert_music_item_delete_confirmation(call: types.CallbackQuery) -> None:

    temp = call.data.split("|")

    concert_music_item_id = int(temp[1])

    action = temp[3]

    concert_music_item = await AsyncORM.get_concert_music_item_by_id(concert_music_item_id)

    if not concert_music_item:
        await call.message.answer(globalTexts.data_notFound_text)
        return
    
    if action == "yes":
        await AsyncORM.delete_concert_music_item(concert_music_item_id)

        await call.message.edit_text(adminWhatIsNewTexts.concert_music_item_actions_delete_confirmation_yes_text.
        format(concert_music_item.name), reply_markup=await adminKeyboards.back_to_selection_menu_kb('what_is_new'))

    elif action == "no":
        await call.message.edit_text(adminWhatIsNewTexts.team_news_item_actions_delete_confirmation_no_text.
        format(concert_music_item.name), reply_markup=await adminKeyboards.back_to_selection_menu_kb('what_is_new'))
'''/Музыка с концерта/'''

'''/Что нового?/'''


def hand_add():
    '''Что нового?'''
    router.callback_query.register(send_what_is_new_selection_menu, lambda c: c.data == 'admin|what_is_new')

    '''Новости команды'''
    router.callback_query.register(send_team_news, lambda c: c.data == 'admin|what_is_new|team_news')
    
    router.callback_query.register(wait_team_news_item_name, lambda c: c.data == 'admin|team_news|add')

    router.message.register(wait_team_news_item_info, StateFilter(WhatIsNewStates.team_news_item_wait_name))

    router.message.register(add_team_news_item, StateFilter(WhatIsNewStates.team_news_item_wait_info))

    router.callback_query.register(show_team_news_item, lambda c: 
    re.match(r"^admin_team_news\|(?P<team_news_item_id>\d+)$", c.data))

    router.callback_query.register(team_news_item_actions, lambda c: 
    re.match(r"^team_news\|(?P<team_news_item_id>\d+)\|(?P<action>replace|delete)$", c.data))

    router.callback_query.register(team_news_item_delete_confirmation, lambda c: 
    re.match(r"^team_news\|(?P<team_news_item_id>\d+)\|delete\|(?P<choice>yes|no)$", c.data))
    '''/Новости команды/'''

    '''Эксклюзивные треки'''
    router.callback_query.register(send_exclusive_tracks, lambda c: c.data == 'admin|what_is_new|exclusive_tracks')
    
    router.callback_query.register(wait_exclusive_track_name, lambda c: c.data == 'admin|exclusive_tracks|add')

    router.message.register(wait_exclusive_track, StateFilter(WhatIsNewStates.exclusive_track_wait_name))

    router.message.register(add_exclusive_track, StateFilter(WhatIsNewStates.exclusive_track_wait_info))

    router.callback_query.register(show_exclusive_track, lambda c: 
    re.match(r"^admin_exclusive_tracks\|(?P<exclusive_track_id>\d+)$", c.data))

    router.callback_query.register(exclusive_track_actions, lambda c: 
    re.match(r"^exclusive_tracks\|(?P<exclusive_track_id>\d+)\|(?P<action>replace|delete)$", c.data))

    router.callback_query.register(exclusive_track_delete_confirmation, lambda c: 
    re.match(r"^exclusive_tracks\|(?P<exclusive_track_id>\d+)\|delete\|(?P<choice>yes|no)$", c.data))
    '''/Эксклюзивные треки/'''

    '''Музыка с концерта'''
    router.callback_query.register(send_concert_music, lambda c: c.data == 'admin|what_is_new|concert_music')
    
    router.callback_query.register(wait_concert_music_item_name, lambda c: c.data == 'admin|concert_music|add')

    router.message.register(wait_concert_music_item, StateFilter(WhatIsNewStates.concert_music_item_wait_name))

    router.message.register(add_concert_music_item, StateFilter(WhatIsNewStates.concert_music_item_wait_info))

    router.callback_query.register(show_concert_music_item, lambda c: 
    re.match(r"^admin_concert_music\|(?P<concert_music_item_id>\d+)$", c.data))

    router.callback_query.register(concert_music_item_actions, lambda c: 
    re.match(r"^concert_music\|(?P<concert_music_item_id>\d+)\|(?P<action>replace|delete)$", c.data))

    router.callback_query.register(concert_music_item_delete_confirmation, lambda c: 
    re.match(r"^concert_music\|(?P<concert_music_item_id>\d+)\|delete\|(?P<choice>yes|no)$", c.data))
    '''/Музыка с концерта/'''
    '''/Что нового?/'''