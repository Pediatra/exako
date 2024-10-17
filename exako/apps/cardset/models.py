from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from exako.database import table_registry


@table_registry.mapped_as_dataclass
class CardSet:
    __tablename__ = 'cardset'

    id: Mapped[int] = mapped_column(
        BigInteger,
        
        init=False,
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    last_review: Mapped[datetime] = mapped_column(
        init=False, onupdate=func.now(), server_default=func.now()
    )
    pinned: Mapped[bool] = mapped_column(default=False)
    language: Mapped[str | None] = mapped_column(String(7), default=None, nullable=True)


@table_registry.mapped_as_dataclass
class Card:
    __tablename__ = 'card'

    id: Mapped[int] = mapped_column(
        BigInteger,
        
        init=False,
        primary_key=True,
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    last_review: Mapped[datetime] = mapped_column(
        init=False, onupdate=func.now(), server_default=func.now()
    )
    cardset_id: Mapped[int] = mapped_column(ForeignKey('cardset.id'), nullable=False)
    term_id: Mapped[int] = mapped_column(ForeignKey('term.id'), nullable=False)
