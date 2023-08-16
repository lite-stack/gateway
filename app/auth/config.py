from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieTransport, JWTStrategy, AuthenticationBackend

from app.auth.manager import get_user_manager
from app.auth.models import User
from app.config import settings

cookie_transport = CookieTransport(cookie_max_age=3600, cookie_name='openstack-user')

def get_jwt_strategy() -> JWTStrategy:
    print(settings.secret_key)
    return JWTStrategy(secret=settings.secret_key, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user()