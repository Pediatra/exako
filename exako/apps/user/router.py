from fastapi_users import FastAPIUsers
from fastapi import HTTPException, status, Depends
from typing import Annotated

from exako.apps.user.models import get_user_manager, User
from exako.apps.user.security import auth_cookie_backend, auth_jwt_backend

fastapi_users = FastAPIUsers(
    get_user_manager,
    [auth_jwt_backend, auth_cookie_backend],
)

current_user = fastapi_users.current_user(active=True)


def current_admin_user(current_user: Annotated[User, Depends(current_user)]):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='not enough permission.',
        )
