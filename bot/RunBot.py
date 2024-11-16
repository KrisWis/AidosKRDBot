from aiogram.types import BotCommand
from InstanceBot import bot, dp
import handlers
import asyncio
import logging
from database.orm import AsyncORM

logger = logging.getLogger(__name__)
logging.basicConfig(filename='Logs.log', level=logging.INFO)

async def on_startup() -> None:

    # Пересоздаём таблицы в базе данных (для тестов).
    await AsyncORM.create_tables()

    # Определяем команды и добавляем их в бота
    commands = [
        BotCommand(command='/start', description='Перезапустить бота'),
    ]

    await bot.set_my_commands(commands)

    handlers.hand_start.hand_add()

    handlers.hand_admin.hand_add()
    
    bot_info = await bot.get_me()

    logging.basicConfig(level=logging.INFO)

    print(f'Бот запущен - @{bot_info.username}')

    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(on_startup())
