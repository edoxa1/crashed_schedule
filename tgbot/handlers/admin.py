from aiogram import Router
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message

from infrastructure.database.repo.requests import RequestsRepo
from tgbot.filters.admin import AdminFilter
from tgbot.keyboards import inline

admin_router = Router()
admin_router.message.filter(AdminFilter())


@admin_router.message(Command(commands=['get_info']))
async def get_user_info(message: Message, command: CommandObject, repo: RequestsRepo):
    await message.answer("User not found")

