from aiogram import types
from InstanceBot import router
from aiogram.filters import CommandStart, StateFilter


# Отправка стартового меню при вводе "/start"
async def start(message: types.Message):
    await message.answer("Дарова")


def hand_add():
    router.message.register(start, StateFilter("*"), CommandStart())
