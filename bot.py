import asyncio
import logging

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder

from tgbot.config import load_config, Config
from tgbot.handlers import routers_list
from tgbot.middlewares.config import ConfigMiddleware
from tgbot.middlewares.database import DatabaseMiddleware
from tgbot.middlewares.courses import ParsedCoursesMiddleware
# from tgbot.middlewares.throttling import ThrottlingMiddleware
from tgbot.services import broadcaster

from infrastructure.database.setup import create_engine, create_session_pool
from infrastructure.services.pdf.parser import PdfParser


async def on_startup(bot: Bot, admin_ids: list[int]):
    await broadcaster.broadcast(bot, admin_ids, "Bot started!")


def register_global_middlewares(dp: Dispatcher, config: Config, courses_list, session_pool=None, storage=None):
    middleware_types = [
        ConfigMiddleware(config),
        DatabaseMiddleware(session_pool),
        ParsedCoursesMiddleware(courses_list)
        # ThrottlingMiddleware(storage)
    ]

    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)


def setup_logging():
    log_level = logging.DEBUG
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=log_level,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


def get_storage(config):
    if config.tg_bot.use_redis:
        return RedisStorage.from_url(
            config.redis.dsn(),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        return MemoryStorage()


async def main():
    setup_logging()

    config = load_config(".env")
    storage = get_storage(config)

    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    dp = Dispatcher(storage=storage)

    dp.include_routers(*routers_list)

    # database
    engine = create_engine(config.db, True)
    session_pool = create_session_pool(engine)

    # parser
    parser = PdfParser(config.misc.pdf_path)
    courses_list = parser.courses

    register_global_middlewares(dp, config, courses_list=courses_list, session_pool=session_pool, storage=storage)

    await on_startup(bot, config.tg_bot.admin_ids)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Бот був вимкнений!")
