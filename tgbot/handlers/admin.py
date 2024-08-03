from aiogram import Router
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message, BufferedInputFile

from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.models.section import Section
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.user import gen
from tgbot.keyboards import inline
from tgbot.services.plotter import create_plot
from tgbot.services.scheduler import check_clash

admin_router = Router()
admin_router.message.filter(AdminFilter())


@admin_router.message(Command(commands=['get_info']))
async def get_user_info(message: Message, command: CommandObject, repo: RequestsRepo):
    await message.answer("User not found")


@admin_router.message(Command(commands=['gen']))
async def gen_with_colour(message: Message, storage: RedisStorage, command: CommandObject):
    if not command.args:
        return
    colour, text_colour = command.args.split()
    cart = await storage.redis.lrange(name=f'cart_{message.from_user.id}', start=0, end=-1)
    if not cart:
        return

    sections = [*Section.from_json_to_generator(cart)]
    if check_clash(sections):
        return

    create_plot(sections, colour, text_colour)
