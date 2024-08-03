from typing import List

from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from infrastructure.models.course import Course
from infrastructure.models.section import Section
from infrastructure.models.types import SectionType


def select_course_keyboard(courses: List[Course]) -> ReplyKeyboardMarkup:
    buttons = []
    for course in courses:
        buttons.append(KeyboardButton(text=course.abbr))

    keyboard = ReplyKeyboardMarkup(keyboard=[buttons], one_time_keyboard=True, resize_keyboard=True)
    return keyboard


def select_course_type(course: Course) -> ReplyKeyboardMarkup:
    buttons = []
    for stype in course.sections.values():
        buttons.append(KeyboardButton(text=stype.get_type()))

    keyboard = ReplyKeyboardMarkup(keyboard=[buttons], one_time_keyboard=True, resize_keyboard=True)
    return keyboard


def select_section_keyboard(stype: SectionType) -> ReplyKeyboardMarkup:
    buttons = []
    for section in stype.sections:
        buttons.append(KeyboardButton(text=section.name))

    keyboard = ReplyKeyboardMarkup(keyboard=[buttons], one_time_keyboard=True, resize_keyboard=True)
    return keyboard
#
#
# def generate_course_types_keyboard(ctypes: List[str]) -> ReplyKeyboardMarkup:
#     kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#     for ctype in ctypes:
#         kb.insert(KeyboardButton(text=ctype))
#
#     return kb
#
#
# def generate_empty_keyboard() -> ReplyKeyboardRemove:
#     return ReplyKeyboardRemove()
