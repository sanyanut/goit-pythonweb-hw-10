from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.models import User
from src.schemas.users import UserModel


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, body: UserModel, avatar: str | None = None) -> User:
        data = body.model_dump()
        hashed_password = data.pop("password")
        new_user = User(**data, hashed_password=hashed_password, avatar=avatar)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def confirmed_email(self, email: str) -> None:
        user = await self.get_user_by_email(email)
        if user:
            user.confirmed = True
            await self.db.commit()

    async def update_avatar(self, email: str, url: str) -> User | None:
        user = await self.get_user_by_email(email)
        if user:
            user.avatar = url
            await self.db.commit()
            await self.db.refresh(user)
        return user

    async def update_token(self, user: User, token: str | None) -> None:
        user.refresh_token = token
        await self.db.commit()
