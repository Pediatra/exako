from fastapi_users import FastAPIUsers

from exako.apps.user.models import get_user_manager
from exako.apps.user.security import auth_cookie_backend, auth_jwt_backend

fastapi_users = FastAPIUsers(
    get_user_manager,
    [auth_jwt_backend, auth_cookie_backend],
)

current_user = fastapi_users.current_user(active=True)
