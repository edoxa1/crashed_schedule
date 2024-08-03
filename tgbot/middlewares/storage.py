from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message

from infrastructure.database.repo.requests import RequestsRepo


class RedisMiddleware(BaseMiddleware):
    def __init__(self, storage: RedisStorage) -> None:
        self.storage = storage

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:

        data['storage'] = self.storage
        result = await handler(event, data)
        return result
