from fastapi import APIRouter, Depends, status, UploadFile, File, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.schemas.users import UserResponse
from src.services.auth import get_current_user
from src.services.upload_avatar import UploadService
from src.services.users import UserService
from src.conf.limiter import limiter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
@limiter.limit("5/minute")
async def read_users_me(request: Request, current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/avatar", response_model=UserResponse)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    public_id = f"ContactsApp/{current_user.email}"
    r = UploadService.upload_image(file.file, public_id)
    user_service = UserService(db)
    user = await user_service.update_avatar(current_user.email, r)
    return user
