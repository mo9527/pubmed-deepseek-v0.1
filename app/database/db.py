# db.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from typing import AsyncGenerator
import sys
from app.util.app_log import logger

try:
    from app.config import CONFIG, CURRENT_ENV
except ImportError:
    print("FATAL ERROR: Could not import configuration module 'config'. Exiting.")
    sys.exit(1)


DATABASE_URL = CONFIG.get('db_config').get('url')

if not DATABASE_URL:
    logger.error("FATAL ERROR: 'database_url' 在配置文件中未找到.")
    sys.exit(1)


# 连接池设置 
POOL_SETTINGS = {
    # pool_pre_ping: True 检查连接是否可用 (防止 MySQL 连接超时断开)
    "pool_pre_ping": True,
    # pool_recycle: 建议设置为低于 MySQL 服务器的 wait_timeout (通常是 3600秒，我们设置为 3500秒)
    "pool_recycle": 3500,
    # pool_size: 连接池大小 (默认为 5，根据并发量调整)
    "pool_size": 10,
    # max_overflow: 连接池溢出数量 (当池满时可以创建的额外连接数)
    "max_overflow": 20,
}

# 是否启用 SQL Echo (仅在 DEBUG 环境启用)
ECHO_SQL = CONFIG.get('log_level', '').upper() == 'DEBUG'

# try:
#     engine = create_engine(
#         DATABASE_URL, 
#         echo=ECHO_SQL,
#         **POOL_SETTINGS
#     )
#     logger.info(f"数据库engine创建成功. 环境: {CURRENT_ENV}")

# except Exception as e:
#     logger.error(f"FATAL ERROR: Failed to create database engine for URL {DATABASE_URL}. Error: {e}")
#     sys.exit(1)


# # 会话session
# SessionLocal = sessionmaker(
#     autocommit=False,       # 事务必须手动提交
#     autoflush=False,        # 除非提交或查询，否则不会自动将更改刷新到数据库
#     bind=engine             # 绑定到上面创建的 Engine
# )
# logger.info("SessionLocal factory 创建成功.")

try:
    engine = create_async_engine(
        DATABASE_URL, 
        echo=ECHO_SQL,                 
        **POOL_SETTINGS
    )
    logger.info(f"数据库engine创建成功. 环境: {CURRENT_ENV}")
except Exception as e:
    logger.error(f"FATAL ERROR: Failed to create async database engine for URL {DATABASE_URL}. Error: {e}")

# 异步 Session 工厂
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False  # 通常用于异步 Session，防止在 commit 后立即访问关系数据时报错
)


# 所有 ORM 模型都需要继承这个 Base
Base = declarative_base()


async def check_db_connection():
    """测试数据库连接"""
    async with AsyncSessionLocal() as session:
        try:
            await session.execute(text("SELECT 1"))
            logger.info("数据库连接正常.")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
    
    
    

async def close_connection():
    """关闭数据库连接。"""
    await engine.dispose()
    logger.info("数据库连接已关闭.")
    
    
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    获取异步数据库会话。
    在请求结束后自动关闭 Session。
    """
    async with AsyncSessionLocal() as session:
        yield session
        
        
        
        
__all__ = [
    "Base",
    "AsyncSessionLocal",
    "engine",
    "check_db_connection",
    "get_db_session",
]   