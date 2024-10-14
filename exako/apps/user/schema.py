from fastapi_users import schemas

from exako.apps.term.constants import Language


class UserRead(schemas.BaseUser[int]):
    name: str
    native_language: Language


class UserCreate(schemas.BaseUserCreate):
    name: str
    native_language: Language
