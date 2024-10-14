from fastapi import Depends
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users.db import BaseUserDatabase
from tortoise import fields, models
from tortoise.exceptions import DoesNotExist


class User(models.Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(index=True, unique=True, null=False, max_length=255)
    hashed_password = fields.CharField(null=False, max_length=1024)
    is_active = fields.BooleanField(default=True, null=False)
    is_superuser = fields.BooleanField(default=False, null=False)
    is_verified = fields.BooleanField(default=False, null=False)
    name = fields.CharField(max_length=50, null=True)
    native_language = fields.CharField(max_length=7)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)


class UserDatabase(BaseUserDatabase):
    def __init__(
        self,
        user_model: User,
    ):
        self.user_model = user_model

    async def get(self, id: int) -> User | None:
        try:
            return await self.user_model.get(id=id)
        except DoesNotExist:
            return None

    async def get_by_email(self, email: str) -> User | None:
        return await self.user_model.filter(email__iexact=email).first()

    async def create(self, create_dict: dict) -> User:
        user = self.user_model(**create_dict)
        await user.save()
        await user.refresh_from_db()
        return user


class UserManager(IntegerIDMixin, BaseUserManager):
    user_db = UserDatabase


async def get_user_db():
    yield UserDatabase(User)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
