from aiogram.filters.callback_data import CallbackData


class StartMenu(CallbackData, prefix='start_menu'):
    action: str


class SelectSection(CallbackData, prefix='section'):
    course_index: int
    name: str
