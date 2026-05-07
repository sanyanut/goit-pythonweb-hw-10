from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repository.users import UserRepository
from src.schemas.users import UserModel
from src.database.models import User

class UserService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.repository.get_user_by_email(email)

    async def create_user(self, body: UserModel) -> User:
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)
        return await self.repository.create_user(body, avatar)

    async def confirmed_email(self, email: str) -> None:
        await self.repository.confirmed_email(email)

    async def update_avatar(self, email: str, url: str) -> User | None:
        return await self.repository.update_avatar(email, url)

    async def update_token(self, user: User, token: str | None) -> None:
        await self.repository.update_token(user, token)
