from aiogram import types
from InstanceBot import router
from aiogram.fsm.context import FSMContext
from utils import userDiscountsTexts, adminDiscountsTexts, globalTexts
from keyboards import adminKeyboards
from helpers import deleteSendedMediaGroup, sendPaginationMessage
from database.orm import AsyncORM
from states.Admin import DiscountsStates
from helpers.albumInfoProcess import albumInfoProcess
from helpers.deleteMessage import deleteMessage
from helpers.mediaGroupSend import mediaGroupSend
import datetime
from RunBot import logger
import re
from aiogram.filters import StateFilter


'''Скидки и акции'''
# Отправка сообщения с меню выбора "Скидки и акции"
async def send_discounts_selection_menu(call: types.CallbackQuery, state: FSMContext) -> None:
    
    await deleteSendedMediaGroup(state, call.from_user.id)

    await call.message.edit_text(userDiscountsTexts.discounts_choice_text,
    reply_markup=await adminKeyboards.discounts_selection_menu_kb())


'''Акции'''
# Отправка сообщения со всеми акциями
async def send_rebates(call: types.CallbackQuery, state: FSMContext) -> None:
    rebates = await AsyncORM.get_all_rebates()
    prefix = "admin_rebates"

    async def getRebatesButtonsAndAmount():
        rebates = await AsyncORM.get_all_rebates()

        buttons = [[types.InlineKeyboardButton(
        text=rebate.name,
        callback_data=f'{prefix}|{rebate.id}')] for rebate in rebates]

        return [buttons, len(rebates)]
    
    await sendPaginationMessage(call, state, rebates, getRebatesButtonsAndAmount,
    prefix, adminDiscountsTexts.rebates_text, 10, [await adminKeyboards.get_kb_addButton('rebates'), 
    await adminKeyboards.get_kb_backToSelectionMenuButton('admin|discounts')])


# Отправка сообщения о том, чтобы администратор прислал название акции
async def wait_rebate_name(call: types.CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(adminDiscountsTexts.wait_rebate_name_text)

    await state.set_state(DiscountsStates.rebate_wait_name)


# Ожидание названия акции. Отправка сообщения о том, чтобы администратор прислал информацию об акции
async def wait_rebate_info(message: types.Message, state: FSMContext):
    rebate_name = message.text

    if rebate_name:
        rebate = await AsyncORM.get_rebate_by_name(rebate_name)

        if not rebate:
            await state.update_data(rebate_name=rebate_name)

            await message.answer(adminDiscountsTexts.wait_rebate_info_text)

            await state.set_state(DiscountsStates.rebate_wait_info)

        else:
            await message.answer(globalTexts.adding_data_error_text)
    else:
        await message.answer(globalTexts.data_isInvalid_text)


# Ожидание информации акции. Добавление акции в базу данных
async def add_rebate(message: types.Message, album: list[types.Message] = [], state: FSMContext = None):
    result = await albumInfoProcess(DiscountsStates.rebate_wait_info, state, message, album)

    if not result:
        await message.answer(globalTexts.data_isInvalid_text)
        return

    user_text = result[0]
    photo_file_ids = result[1]
    video_file_ids = result[2]
    now = datetime.datetime.now()
    data = await state.get_data()

    if "rebate_replace_id" in data:
        rebate_replace_id = int(data["rebate_replace_id"])

        await AsyncORM.change_rebate_info(rebate_replace_id,
        user_text, photo_file_ids, video_file_ids)

        rebate = await AsyncORM.get_rebate_by_id(rebate_replace_id)

        await message.answer(adminDiscountsTexts.change_rebate_success_text
        .format(rebate.name), reply_markup=await adminKeyboards.back_to_admin_menu_kb())
    else:
        try:
            await AsyncORM.add_rebate(data["rebate_name"], now, user_text, photo_file_ids, video_file_ids)

            await message.answer(adminDiscountsTexts.add_rebate_success_text,
            reply_markup=await adminKeyboards.back_to_admin_menu_kb())
        except Exception as e:
            logger.info(e)
            await message.answer(globalTexts.adding_data_error_text)

    await state.clear()


# Отправка сообщения с информацией об акции и возможностью удаления/изменения информации
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
        reply_markup=await adminKeyboards.actions_kb(rebate.id, 'rebates'))
    else:
        await call.message.answer(globalTexts.data_notFound_text)


# Обработка изменения/удаления информации об акции
async def rebate_actions(call: types.CallbackQuery, state: FSMContext) -> None:

    temp = call.data.split("|")

    rebate_id = int(temp[1])

    action = temp[2]

    rebate = await AsyncORM.get_rebate_by_id(rebate_id)

    if not rebate:
        await call.message.answer(globalTexts.data_notFound_text)
        return
    
    if action == "replace":
        await call.message.edit_text(adminDiscountsTexts.rebate_actions_edit_text)
        await state.update_data(rebate_replace_id=rebate_id)

        await state.set_state(DiscountsStates.rebate_wait_info)

    elif action == "delete":
        await call.message.edit_text(adminDiscountsTexts.rebate_actions_delete_confirmation_text.
        format(rebate.name),
        reply_markup=await adminKeyboards.delete_confirmation_kb(rebate.id, 'rebates'))


# Обработка подтверждения/отклонения удаления информации об акции
async def rebate_delete_confirmation(call: types.CallbackQuery) -> None:

    temp = call.data.split("|")

    rebate_id = int(temp[1])

    action = temp[3]

    rebate = await AsyncORM.get_rebate_by_id(rebate_id)

    if not rebate:
        await call.message.answer(globalTexts.data_notFound_text)
        return
    
    if action == "yes":
        await AsyncORM.delete_rebate(rebate_id)

        await call.message.edit_text(adminDiscountsTexts.rebate_actions_delete_confirmation_yes_text.
        format(rebate.name), reply_markup=await adminKeyboards.back_to_selection_menu_kb('discounts'))

    elif action == "no":
        await call.message.edit_text(adminDiscountsTexts.rebate_actions_delete_confirmation_no_text.
        format(rebate.name), reply_markup=await adminKeyboards.back_to_selection_menu_kb('discounts'))
'''/Акции/'''
'''/Скидки и акции/'''


def hand_add():
    '''Скидки и акции'''
    router.callback_query.register(send_discounts_selection_menu, lambda c: c.data == 'admin|discounts')
    
    '''Акции'''
    router.callback_query.register(send_rebates, lambda c: c.data == 'admin|discounts|rebates')
    
    router.callback_query.register(wait_rebate_name, lambda c: c.data == 'admin|rebates|add')

    router.message.register(wait_rebate_info, StateFilter(DiscountsStates.rebate_wait_name))

    router.message.register(add_rebate, StateFilter(DiscountsStates.rebate_wait_info))

    router.callback_query.register(show_rebate, lambda c: 
    re.match(r"^admin_rebates\|(?P<rebate_id>\d+)$", c.data))

    router.callback_query.register(rebate_actions, lambda c: 
    re.match(r"^rebates\|(?P<rebate_id>\d+)\|(?P<action>replace|delete)$", c.data))

    router.callback_query.register(rebate_delete_confirmation, lambda c: 
    re.match(r"^rebates\|(?P<rebate_id>\d+)\|delete\|(?P<choice>yes|no)$", c.data))
    '''/Акции/'''
    '''/Скидки и акции/'''