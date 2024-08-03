from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.handlers.user import CourseSelectionForm
from tgbot.keyboards import inline

start_router = Router()


@start_router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer(f'Hello, {message.from_user.full_name}! \n'
                         f'Enter course abbreviation or click buttons below!',
                         reply_markup=inline.start_keyboard())
    await state.set_state(CourseSelectionForm.searching_course)
