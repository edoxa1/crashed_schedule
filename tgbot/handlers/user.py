import logging
from typing import List

from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import random

from infrastructure.database.repo.requests import RequestsRepo
from infrastructure.models.course import Course
from infrastructure.services.pdf.repo import CoursesRepo
from tgbot.keyboards import inline, reply
from tgbot.services import generate

user_router = Router()


class CourseSelectionForm(StatesGroup):
    searching_course = State()
    selecting_course = State()
    selecting_type = State()
    selecting_section = State()


@user_router.message(CommandStart())
async def user_start(message: Message, state: FSMContext):
    await message.answer("Enter course abbreviation")
    await state.set_state(CourseSelectionForm.searching_course)


@user_router.message(CourseSelectionForm.searching_course)
async def search_abbreviation(message: Message, courses: CoursesRepo, state: FSMContext):
    found_courses = courses.search_course(query=message.text)
    if not found_courses:
        await message.answer(f"No results for <i>{message.text}</i>")
        return

    await message.answer(generate.found_courses_text(found_courses),
                         reply_markup=reply.select_course_keyboard(found_courses))
    await state.set_state(CourseSelectionForm.selecting_course)


@user_router.message(CourseSelectionForm.selecting_course)
async def get_abbreviation(message: Message, courses: CoursesRepo, state: FSMContext):
    course = courses.get_course_by_abbr(message.text)

    if not course:
        await search_abbreviation(message, courses, state)
        return

    await message.answer("Select type:", reply_markup=reply.select_course_type(course))

    await state.update_data({'course': course})
    await state.set_state(CourseSelectionForm.selecting_type)


@user_router.message(CourseSelectionForm.selecting_type)
async def get_stype(message: Message, courses: CoursesRepo, state: FSMContext):
    course: Course = (await state.get_data())['course']
    selected_type = message.text

    if selected_type not in course.sections.keys():
        await state.set_state(CourseSelectionForm.searching_course)
        await search_abbreviation(message, courses, state)
        return

    sections = course.sections[selected_type]
    await message.answer(generate.course_type_sections_text(sections),
                         reply_markup=reply.select_section_keyboard(sections))
    await state.update_data({'stype': selected_type})
    await state.set_state(CourseSelectionForm.selecting_section)


@user_router.message(CourseSelectionForm.selecting_section)
async def get_section(message: Message, repo: RequestsRepo, courses: CoursesRepo, state: FSMContext):
    course: Course = (await state.get_data())['course']
    selected_type = (await state.get_data())['stype']
    selected_section = message.text

    # await repo.carts.add_item_to_cart(user_id=message.from_user.id, item_id=)

    for section in course.sections[selected_type].sections:
        if section.course_type == selected_section:
            await message.answer(f"{section.abbr} [{section.course_type}] was added in your cart! "
                                 f"\n\nAdd another section if you wish. "
                                 "Enter course abbreviation otherwise",
                                 reply_markup=reply.select_course_type(course))
            await state.set_state(CourseSelectionForm.selecting_type)
            return

    await state.set_state(CourseSelectionForm.searching_course)
    await search_abbreviation(message, courses, state)

