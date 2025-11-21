from functools import wraps
from sqlalchemy.ext.asyncio import AsyncSession


def transactional(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        session: AsyncSession = kwargs.get("session")
        if session is None:
            raise RuntimeError("AsyncSession must be passed into service method.")

        try:
            result = await func(*args, **kwargs)
            await session.commit()
            return result
        except Exception:
            await session.rollback()
            raise

    return wrapper
