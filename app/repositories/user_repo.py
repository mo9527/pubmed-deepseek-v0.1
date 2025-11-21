import secrets
import string
from datetime import datetime
from typing import Optional

from fastapi.exceptions import HTTPException

from app.core.crud import CRUDBase
from models.user_model import User
from ..schemas.users_schema import UserCreate, UserUpdate


class UserRepository(CRUDBase[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(model=User)

    async def get_by_mobile(self, mobile: str) -> User | None:
        with self.session as s:
            return s.query(self.model).filter(User.mobile==mobile).first()

    async def get_by_username(self, username: str) -> User | None:
        with self.session as s:
            return await s.query(self.model).filter(User.name==username).first()

    async def get_by_email(self, email: str) -> User | None:
        with self.session as s:
            return await s.query(User).filter(User.email==email).first()

    async def create_user(self, obj_in: UserCreate) -> User:
        obj = await self.create(obj_in)
        return obj

    async def update_last_login(self, id: int) -> None:
        user:User = await self.get(id=id)
        user.last_login = datetime.now()
        await user.save()

    def _generate_secure_password(self, length: int = 12) -> str:
        """生成安全的随机密码"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        return password


user_repository = UserRepository()
