from aiogram import Router, F, html
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import CallbackQuery

from infrastructure.models.section import Section
from infrastructure.services.pdf.repo import CoursesRepo
from tgbot.keyboards import inline
from tgbot.services import callback
from tgbot.services.plotter import DAY_NAMES, DAYS

cart_router = Router()


@cart_router.callback_query(callback.StartMenu.filter(F.action == 'cart'))
async def show_cart(call: CallbackQuery, courses: CoursesRepo, state: FSMContext, storage: RedisStorage):
    cart = await storage.redis.lrange(name=f'cart_{call.from_user.id}', start=0, end=-1)
    if not cart:
        await call.message.edit_text("Your cart is empty.", reply_markup=inline.back())
        return
    # text = 'Your cart: \n'
    # for section in Section.from_json_to_generator(cart):
    #     text += section.get_info() + '\n'
    text = text_schedule(cart)
    await call.message.edit_text(text, reply_markup=inline.back())


def text_schedule(cart: list[str]) -> str:
    text = ''
    sections: list[Section] = Section.from_json_to_list(cart)
    for (day_letter, day_name) in zip(DAYS, DAY_NAMES):
        day_text = ''
        sections_per_day = []
        for section in sections:
            for time in section.weektimes:
                if time.day == day_letter:
                    sections_per_day.append((time.start, time.end, section))

        sections_per_day.sort(key=sort_by_time)
        for counter, section in enumerate(sections_per_day, start=1):
            day_text += f'{section[-1].get_day_info((section[0], section[1]))}\n'

        text += html.bold(day_name) + ':\n' + day_text + '\n' if day_text != '' else ''
    return html.pre(text)


def sort_by_time(item: str) -> int:
    start = item[0]
    return int(start.split(':')[0])
