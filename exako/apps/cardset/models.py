from datetime import datetime
from uuid import UUID

import sqlmodel as sm


class CardSet(sm.SQLModel, table=True):
    __tablename__ = 'cardset'

    id: int | None = sm.Field(
        default=None,
        sa_column=sm.Column(sm.BigInteger, primary_key=True),
    )
    user_id: UUID = sm.Field(nullable=False)
    name: str = sm.Field(max_length=256, nullable=False)
    created_at: datetime = sm.Field(default_factory=sm.func.now, nullable=False)
    last_review: datetime = sm.Field(
        default_factory=sm.func.now,
        sa_column_kwargs={'onupdate': sm.func.now()},
        nullable=False,
    )
    pinned: bool = sm.Field(default=False)
    language: str | None = sm.Field(default=None, max_length=7)


class Card(sm.SQLModel, table=True):
    __tablename__ = 'card'

    id: int | None = sm.Field(
        default=None,
        sa_column=sm.Column(sm.BigInteger, primary_key=True),
    )
    note: str | None = sm.Field(default=None, nullable=True)
    created_at: datetime = sm.Field(default_factory=sm.func.now, nullable=False)
    last_review: datetime = sm.Field(
        default_factory=sm.func.now,
        sa_column_kwargs={'onupdate': sm.func.now()},
        nullable=False,
    )
    cardset_id: int = sm.Field(foreign_key='cardset.id', nullable=False)
    term_id: int = sm.Field(foreign_key='term.id', nullable=False)
