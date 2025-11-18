import asyncio
import os
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

from dotenv import load_dotenv

from app.handlers import routers

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename='bot.log',
    filemode='a'
)

bot = Bot(token=os.getenv('TOKEN'),
          default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()
dp.include_routers(*routers)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Bot started")
    try:
        asyncio.run(main())

    except (SystemError, KeyboardInterrupt) as e:
        print(f"Unexpected bot stop: {e}")
    
    print("Bot stopped")