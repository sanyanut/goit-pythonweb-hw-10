from fastapi import APIRouter, Depends, HTTPException, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas.users import UserModel, UserResponse, TokenModel, RefreshTokenModel, RequestEmail
from src.services.users import UserService
from src.services.auth import Hash, create_access_token, get_email_from_token, create_refresh_token, decode_refresh_token
from src.services.email import send_email

router = APIRouter(prefix="/auth", tags=["auth"])
hash_handler = Hash()

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    exist_user = await user_service.get_user_by_email(body.email)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = hash_handler.get_password_hash(body.password)
    new_user = await user_service.create_user(body)
    background_tasks.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not hash_handler.verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    
    access_token = await create_access_token(data={"sub": user.email})
    refresh_token = await create_refresh_token(data={"sub": user.email})
    await user_service.update_token(user, refresh_token)
    return {"access_token": access_token, "token_type": "bearer"}

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
security = HTTPBearer()

@router.get("/refresh_token", response_model=RefreshTokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: AsyncSession = Depends(get_db)):
    token = credentials.credentials
    email = await decode_refresh_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user.refresh_token != token:
        await user_service.update_token(user, None)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await create_access_token(data={"sub": email})
    refresh_token = await create_refresh_token(data={"sub": email})
    await user_service.update_token(user, refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await user_service.confirmed_email(email)
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}
