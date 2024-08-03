from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from infrastructure.models.section import Section
from infrastructure.models.types import SectionType
from tgbot.services import callback
from tgbot.services.callback import StartMenu


def start_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text='My Cart🛒', callback_data=StartMenu(action='cart'))
    keyboard.button(text='Show schedule📅', callback_data=StartMenu(action='schedule'))
    keyboard.adjust(1, 1)

    return keyboard.as_markup()


def back() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text='Back🔙', callback_data=StartMenu(action='back'))

    return keyboard.as_markup()


def selecting_sections(index: int, sections: SectionType) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    for section in sections:
        keyboard.button(text=f'{section.name}',
                        callback_data=callback.SelectSection(course_index=index, name=section.name))

    return keyboard.as_markup(resize_keyboard=True)
