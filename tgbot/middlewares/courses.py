from typing import Callable, Dict, Any, Awaitable, List

from aiogram import BaseMiddleware
from aiogram.types import Message

from infrastructure.services.pdf.repo import CoursesRepo
from infrastructure.models.course import Course


class ParsedCoursesMiddleware(BaseMiddleware):
    def __init__(self, courses: List[Course]) -> None:
        self.repo = CoursesRepo(courses)

    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message, data: Dict[str, Any]
                       ) -> Any:
        data["courses"] = self.repo
        result = await handler(event, data)
        return result
