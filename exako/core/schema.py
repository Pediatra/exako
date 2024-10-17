from pydantic import BaseModel


class NotAuthenticated(BaseModel):
    detail: str = 'could not validate credentials.'


class NotFound(BaseModel):
    detail: str = 'object not found.'


class PermissionDenied(BaseModel):
    detail: str = 'not enough permissions.'
