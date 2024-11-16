from aiogram.filters import Filter
from aiogram import types
from aiogram.fsm.context import FSMContext
from Config import admins
from utils import globalText


# Создаём собственный фильтр на проверку того, что юзер - админ
class AdminFilter(Filter):
    async def __call__(self, message: types.Message, state: FSMContext) -> bool:
        user_id = message.from_user.id

        if user_id in admins:
            return True
        else:
            await message.answer(globalText.rightsError_text)
            return False
