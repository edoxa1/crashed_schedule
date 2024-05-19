from datetime import datetime
from typing import Optional, List

from sqlalchemy import func, text
from sqlalchemy import BIGINT, Boolean, false, Integer, ARRAY, SMALLINT, String, TIMESTAMP
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import ForeignKey

from .base import Base, TimestampMixin, TableNameMixin


class Cart(Base, TimestampMixin, TableNameMixin):
    __tablename__ = "carts"

    user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=False)
    cart: Mapped[List[int]] = mapped_column(ARRAY(SMALLINT))

    def __repr__(self):
        return f"User {self.user_id}\n" \
               f"Cart: {self.cart}"
