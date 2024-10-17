from datetime import datetime

from fastapi import Depends
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy import DateTime, String, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from exako.database import get_async_session, table_registry


@table_registry.mapped
class User(SQLAlchemyBaseUserTableUUID):
    __tablename__ = 'user'

    name: Mapped[str] = mapped_column(String(50))
    native_language: Mapped[str] = mapped_column(String(7))
    created_at: Mapped[datetime] = mapped_column(DateTime   ,server_default=func.now())


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


class UserManager(IntegerIDMixin, BaseUserManager):
    pass


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
