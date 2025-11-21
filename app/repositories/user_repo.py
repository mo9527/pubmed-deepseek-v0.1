import secrets
import string
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy import select, update as sql_update
from fastapi.exceptions import HTTPException
from app.core.crud import CRUDBase
from models.user_model import User
from ..schemas.users_schema import UserCreate, UserUpdate


class UserRepository(CRUDBase[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(model=User)

    async def get_by_mobile(self, db: AsyncSession, mobile: str) -> User | None:
        result: Result = await db.execute(
            select(User).where(User.mobile == mobile)
        )
        # 获取结果
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        result: Result = await db.execute(
            select(User).where(User.name == username)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        result: Result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create_user(self, db: AsyncSession, obj_in: UserCreate) -> User:
        return await super().create(db, obj_in)

    async def update_last_login(self, db: AsyncSession, id: int) -> None:
        stmt = (
            sql_update(User)
            .where(User.id == id)
            .values(last_login=datetime.now())
        )
        await db.execute(stmt)

    def _generate_secure_password(self, db: AsyncSession, length: int = 12) -> str:
        """生成安全的随机密码"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        return password


user_repository = UserRepository()
