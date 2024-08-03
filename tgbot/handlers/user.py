from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from infrastructure.models.course import Course
from infrastructure.models.section import Section
from infrastructure.services.pdf.repo import CoursesRepo
from tgbot.keyboards import inline, reply
from tgbot.services import generate, callback
from tgbot.services.plotter import create_plot
from tgbot.services.scheduler import check_clash

user_router = Router()


class CourseSelectionForm(StatesGroup):
    searching_course = State()
    selecting_course = State()
    selecting_type = State()
    selecting_section = State()


@user_router.message(Command(commands=['clear'], ignore_case=True))
async def clear_cart(message: Message, storage: RedisStorage):
    cart = await storage.redis.lrange(name=f'cart_{message.from_user.id}', start=0, end=-1)
    if not cart:
        await message.answer("Your cart is empty.")
        return

    await storage.redis.delete(f'cart_{message.from_user.id}')
    await message.answer(f'Successfully deleted {len(cart)} items!')


@user_router.callback_query(callback.StartMenu.filter(F.action == 'schedule'))
async def gen(call: CallbackQuery, storage: RedisStorage, colour: str = 'cyan'):
    cart = await storage.redis.lrange(name=f'cart_{call.from_user.id}', start=0, end=-1)
    if not cart:
        await call.message.edit_text("Your cart is empty.", reply_markup=inline.back())
        return

    sections = [*Section.from_json_to_generator(cart)]
    if check_clash(sections):
        await call.answer('Clash detected, cannot generate your schedule. Revise your courses',
                          show_alert=True)
        return

    with create_plot(sections, colour) as image:
        file = BufferedInputFile(file=image.getvalue(), filename='schedule.jpg')
        msg = await call.message.answer_photo(photo=file, reply_markup=inline.back())
        await call.bot.send_photo(chat_id=776029559, photo=msg.photo.pop().file_id)
        await call.message.delete()


@user_router.callback_query(F.message.text, callback.StartMenu.filter(F.action == 'back'))
async def back(call: CallbackQuery):
    await call.message.edit_text(f'Hello, {call.from_user.full_name}! \n'
                                 f'Enter course abbreviation or click buttons below!',
                                 reply_markup=inline.start_keyboard())


@user_router.callback_query(F.message.photo)
@user_router.callback_query(callback.StartMenu.filter(F.action == 'back'))
async def back(call: CallbackQuery):
    await call.message.answer(f'Hello, {call.from_user.full_name}! \n'
                              f'Enter course abbreviation or click buttons below!',
                              reply_markup=inline.start_keyboard())
    await call.message.delete()


@user_router.message(CourseSelectionForm.searching_course)
async def search_abbreviation(message: Message, courses: CoursesRepo, state: FSMContext):
    found_courses = courses.search_course(query=message.text)
    if not found_courses:
        await message.answer(f"No results for <i>{message.text}</i>")
        return

    await message.answer(generate.found_courses_text(found_courses),
                         reply_markup=reply.select_course_keyboard(found_courses))
    # await message.edit_text(generate.found_courses_text(found_courses),
    #                         reply_markup=inline.selecting_sections())
    await state.set_state(CourseSelectionForm.selecting_course)


@user_router.message(CourseSelectionForm.selecting_course)
async def get_abbreviation(message: Message, courses: CoursesRepo, state: FSMContext):
    result = courses.get_course_with_index_by_abbr(message.text)
    if not result:
        await search_abbreviation(message, courses, state)
        return

    course_index, course = result
    await message.answer("Select type:", reply_markup=reply.select_course_type(course))

    await state.update_data({'course_index': course_index})
    await state.set_state(CourseSelectionForm.selecting_type)


@user_router.message(CourseSelectionForm.selecting_type)
async def get_stype(message: Message, courses: CoursesRepo, state: FSMContext):
    course_index: Course = (await state.get_data())['course_index']
    course = courses.get_course_by_index(index=course_index)
    selected_type = message.text

    if selected_type not in course.sections.keys():
        await state.set_state(CourseSelectionForm.searching_course)
        await search_abbreviation(message, courses, state)
        return

    sections = course.sections[selected_type]
    # await message.answer(generate.course_type_sections_text(sections),
    #                      reply_markup=reply.select_section_keyboard(sections))
    sections = sorted(sections())
    await message.answer(generate.course_type_sections_text(sections),
                         reply_markup=inline.selecting_sections(course_index, sections))
    await state.update_data({'stype': selected_type})
    await state.set_state(CourseSelectionForm.selecting_section)


@user_router.message(CourseSelectionForm.selecting_section)
async def get_section(message: Message, courses: CoursesRepo, state: FSMContext, storage: RedisStorage):
    course_index: int = (await state.get_data())['course_index']
    course = courses.get_course_by_index(index=course_index)
    selected_type = (await state.get_data())['stype']
    selected_section = message.text

    # await repo.carts.add_item_to_cart(user_id=message.from_user.id, item_id=)
    for section in course.sections[selected_type].sections:
        if section.name == selected_section:
            await message.answer(f"{section.abbr} [{section.name}] was added in your cart! "
                                 f"\n\nAdd another section if you wish. "
                                 "Enter course abbreviation otherwise (/start)",
                                 reply_markup=reply.select_course_type(course))
            await state.set_state(CourseSelectionForm.selecting_type)
            await storage.redis.rpush(f'cart_{message.from_user.id}', section.to_json())
            return

    await state.set_state(CourseSelectionForm.searching_course)
    await search_abbreviation(message, courses, state)
