from typing import Optional, List
from datetime import datetime

from sqlalchemy import select, func, update
from sqlalchemy.dialects.postgresql import insert

from infrastructure.database.models.cart import Cart
from infrastructure.database.repo.base import BaseRepo


class CartRepo(BaseRepo):
    async def add_user(self, user_id: int, cart: list) -> Cart:
        insert_stmt = (
            insert(Cart)
            .values(
                user_id=user_id,
                cart=cart
            )
            .on_conflict_do_update(
                index_elements=[Cart.user_id],
                set_=dict(
                    cart=cart
                )
            )
            .returning(Cart)
        )
        result = await self.session.execute(insert_stmt)

        await self.session.commit()
        return result.scalar_one_or_none()

    async def get_user_cart(self, user_id: int) -> List[int]:
        stmt = (
            select(Cart.cart)
            .where(Cart.user_id == user_id)
        )

        result = (await self.session.execute(stmt)).scalar_one()
        return result if result else None

    async def add_item_to_cart(self, user_id: int, item_id: int):
        cart = await self.get_user_cart(user_id)
        if not cart:
            cart = []

        cart.append(item_id)
        stmt = (
            update(Cart)
            .where(Cart.user_id == user_id)
            .values(
                cart=cart,
                last_used=datetime.now()
            )
        )

        result = await self.session.execute(stmt)

        await self.session.commit()
