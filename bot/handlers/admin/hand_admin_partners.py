from aiogram import types
from InstanceBot import router
from aiogram.fsm.context import FSMContext
from utils import adminPartnersTexts, userPartnersTexts, globalTexts
from keyboards import adminKeyboards
from helpers import sendPaginationMessage
from database.orm import AsyncORM
from states.Admin import PartnersStates
from helpers.albumInfoProcess import albumInfoProcess
from helpers.deleteMessage import deleteMessage
from helpers.mediaGroupSend import mediaGroupSend
import datetime
from RunBot import logger
import re
from aiogram.filters import StateFilter


'''Партнёры'''
# Отправка сообщения со всеми акциями
async def send_partners(call: types.CallbackQuery, state: FSMContext) -> None:
    partners = await AsyncORM.get_all_partners()
    prefix = "admin_partners"

    async def getPartnersButtonsAndAmount():
        partners = await AsyncORM.get_all_partners()

        buttons = [[types.InlineKeyboardButton(
        text=partner.name,
        callback_data=f'{prefix}|{partner.id}')] for partner in partners]

        return [buttons, len(partners)]
    
    await sendPaginationMessage(call, state, partners, getPartnersButtonsAndAmount,
    prefix, adminPartnersTexts.partners_text, 10, [await adminKeyboards.get_kb_addButton('partners'), 
    await adminKeyboards.get_back_to_admin_menu_kb_button()])


# Отправка сообщения о том, чтобы администратор прислал название партнёра
async def wait_partner_name(call: types.CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(adminPartnersTexts.wait_partner_name_text)

    await state.set_state(PartnersStates.partner_wait_name)


# Ожидание названия партнёра. Отправка сообщения о том, чтобы администратор прислал информацию о партнёре
async def wait_partner_info(message: types.Message, state: FSMContext):
    partner_name = message.text

    if partner_name:
        partner = await AsyncORM.get_partner_by_name(partner_name)

        if not partner:
            await state.update_data(partner_name=partner_name)

            await message.answer(adminPartnersTexts.wait_partner_info_text)

            await state.set_state(PartnersStates.partner_wait_info)

        else:
            await message.answer(globalTexts.adding_data_error_text)
    else:
        await message.answer(globalTexts.data_isInvalid_text)


# Ожидание информации о партнёре. Добавление партнёра в базу данных
async def add_partner(message: types.Message, album: list[types.Message] = [], state: FSMContext = None):
    result = await albumInfoProcess(PartnersStates.partner_wait_info, state, message, album)

    if not result:
        return

    user_text = result[0]
    photo_file_ids = result[1]
    video_file_ids = result[2]
    now = datetime.datetime.now()
    data = await state.get_data()

    if "partner_replace_id" in data:
        partner_replace_id = int(data["partner_replace_id"])

        await AsyncORM.change_partner_info(partner_replace_id,
        user_text, photo_file_ids, video_file_ids)

        partner = await AsyncORM.get_partner_by_id(partner_replace_id)

        await message.answer(adminPartnersTexts.change_partner_success_text
        .format(partner.name), reply_markup=await adminKeyboards.back_to_admin_menu_kb())
    else:
        try:
            await AsyncORM.add_partner(data["partner_name"], now, user_text, photo_file_ids, video_file_ids)

            await message.answer(adminPartnersTexts.add_partner_success_text,
            reply_markup=await adminKeyboards.back_to_admin_menu_kb())
        except Exception as e:
            logger.info(e)
            await message.answer(globalTexts.adding_data_error_text)

    await state.clear()


# Отправка сообщения с информацией о партнёре и возможностью удаления/изменения информации
async def show_partner(call: types.CallbackQuery, state: FSMContext) -> None:
    await deleteMessage(call)

    temp = call.data.split("|")

    partner_id = int(temp[1])

    partner = await AsyncORM.get_partner_by_id(partner_id)

    if partner:
        await mediaGroupSend(call, state, partner.photo_file_ids, partner.video_file_ids)

        answer_message_text = userPartnersTexts.show_partners_withoutText_text.format(partner.name)

        if partner.text:
            if not partner.photo_file_ids and not partner.video_file_ids:
                answer_message_text = userPartnersTexts.show_partners_text.format(partner.name, partner.text)
            else:
                answer_message_text = userPartnersTexts.show_partners_withImages_text.format(partner.name, partner.text)

        await call.message.answer(answer_message_text,
        reply_markup=await adminKeyboards.actions_kb(partner.id, 'partners', 'admin|partners'))
    else:
        await call.message.answer(globalTexts.data_notFound_text)


# Обработка изменения/удаления информации о партнёре
async def partner_actions(call: types.CallbackQuery, state: FSMContext) -> None:

    temp = call.data.split("|")

    partner_id = int(temp[1])

    action = temp[2]

    partner = await AsyncORM.get_partner_by_id(partner_id)

    if not partner:
        await call.message.answer(globalTexts.data_notFound_text)
        return
    
    if action == "replace":
        await call.message.edit_text(adminPartnersTexts.partner_actions_edit_text)
        await state.update_data(partner_replace_id=partner_id)

        await state.set_state(PartnersStates.partner_wait_info)

    elif action == "delete":
        await call.message.edit_text(adminPartnersTexts.partner_actions_delete_confirmation_text.
        format(partner.name),
        reply_markup=await adminKeyboards.delete_confirmation_kb(partner.id, 'partners'))


# Обработка подтверждения/отклонения удаления информации о партнёре
async def partner_delete_confirmation(call: types.CallbackQuery) -> None:

    temp = call.data.split("|")

    partner_id = int(temp[1])

    action = temp[3]

    partner = await AsyncORM.get_partner_by_id(partner_id)

    if not partner:
        await call.message.answer(globalTexts.data_notFound_text)
        return
    
    if action == "yes":
        await AsyncORM.delete_partner(partner_id)

        await call.message.edit_text(adminPartnersTexts.partner_actions_delete_confirmation_yes_text.
        format(partner.name), reply_markup=await adminKeyboards.back_to_selection_menu_kb('partners'))

    elif action == "no":
        await call.message.edit_text(adminPartnersTexts.partner_actions_delete_confirmation_no_text.
        format(partner.name), reply_markup=await adminKeyboards.back_to_selection_menu_kb('partners'))
'''/Партнёры/'''


def hand_add():
    '''Партнёры'''
    router.callback_query.register(send_partners, lambda c: c.data == 'admin|partners')
    
    router.callback_query.register(wait_partner_name, lambda c: c.data == 'admin|partners|add')

    router.message.register(wait_partner_info, StateFilter(PartnersStates.partner_wait_name))

    router.message.register(add_partner, StateFilter(PartnersStates.partner_wait_info))

    router.callback_query.register(show_partner, lambda c: 
    re.match(r"^admin_partners\|(?P<partner_id>\d+)$", c.data))

    router.callback_query.register(partner_actions, lambda c: 
    re.match(r"^partners\|(?P<partner_id>\d+)\|(?P<action>replace|delete)$", c.data))

    router.callback_query.register(partner_delete_confirmation, lambda c: 
    re.match(r"^partners\|(?P<partner_id>\d+)\|delete\|(?P<choice>yes|no)$", c.data))
    '''/Партнёры/'''