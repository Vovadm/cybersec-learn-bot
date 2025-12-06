import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config import settings
from app.db.lessons_loader import load_lessons_from_json
from app.handlers import router
from app.db.db import Base, engine


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def main():
    # Сначала создаём таблицы
    await init_db()
    await load_lessons_from_json("src/data/lessons.json")

    # Потом запускаем бота
    bot = Bot(token=settings.token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("successful exit")
