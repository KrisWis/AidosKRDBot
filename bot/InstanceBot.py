from aiogram import Dispatcher, Router, Bot
from aiogram.fsm.storage.memory import MemoryStorage
import os
from aiogram.client.default import DefaultBotProperties
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

storage = MemoryStorage()

bot = Bot(token=os.getenv("BOT_API_TOKEN"), default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()
router = Router()
dp.include_router(router)