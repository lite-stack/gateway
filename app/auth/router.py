from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.config import current_user, fastapi_users
from app.auth.db_service import get_users
from app.auth.models import User
from app.auth.schemas import UserRead, UserUpdate
from app.dependencies import get_async_session


router = fastapi_users.get_users_router(UserRead, UserUpdate)

@router.get("", response_model=list[UserRead])
async def list_users(
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        if not user.is_superuser:
            raise HTTPException(status_code=403, detail="Forbidden")

        users = await get_users(session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get users: {e}")

    return users
