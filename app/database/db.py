# db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sys
from app.app_log import logger

# ----------------------------------------------------
# ⚠️ 1. 导入配置模块 (假设 config.py 已经处理了环境选择)
# ----------------------------------------------------
try:
    from app.config.config import CONFIG, CURRENT_ENV
except ImportError:
    print("FATAL ERROR: Could not import configuration module 'config'. Exiting.")
    sys.exit(1)


# --- 2. 数据库连接信息检查 ---
DATABASE_URL = CONFIG.get('db_config').get('url')

if not DATABASE_URL:
    logger.error("FATAL ERROR: 'database_url' key is missing in the current environment config.")
    sys.exit(1)

# ----------------------------------------------------
# 3. SQLAlchemy Engine 配置
# ----------------------------------------------------

# 连接池设置 (推荐用于生产环境 MySQL)
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

try:
    engine = create_engine(
        DATABASE_URL, 
        echo=ECHO_SQL,
        **POOL_SETTINGS
    )
    logger.info(f"Database Engine initialized successfully for environment: {CURRENT_ENV}")

except Exception as e:
    logger.error(f"FATAL ERROR: Failed to create database engine for URL {DATABASE_URL}. Error: {e}")
    sys.exit(1)


# ----------------------------------------------------
# 4. SessionLocal (会话工厂)
# ----------------------------------------------------
# SessionLocal 是一个工厂类，用于创建独立的数据库会话。
# 在 FastAPI 中，应该在每个请求开始时创建一个会话，并在请求结束时关闭。
SessionLocal = sessionmaker(
    autocommit=False,       # 事务必须手动提交
    autoflush=False,        # 除非提交或查询，否则不会自动将更改刷新到数据库
    bind=engine             # 绑定到上面创建的 Engine
)
logger.info("SessionLocal factory created.")


# ----------------------------------------------------
# 5. 模型基类 (Declarative Base)
# ----------------------------------------------------
# 所有 ORM 模型都需要继承这个 Base
Base = declarative_base()


# ----------------------------------------------------
# 6. 辅助函数 (初始化/测试)
# ----------------------------------------------------

def check_db_connection():
    """测试数据库连接是否可用。"""
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        logger.info("Database connection test passed.")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed. Error: {e}")
        return False

def init_db(check_before_create: bool = False):
    """
    初始化数据库（创建所有表）。
    警告：仅用于开发环境或首次设置。
    生产环境应使用 Alembic。
    """
    if check_before_create and not check_db_connection():
        logger.warning("Skipping table creation: Database connection is unavailable.")
        return

    logger.info("Attempting to create all declared database tables...")
    
    # ⚠️ 确保在此之前，所有模型文件都被导入，以便 Base.metadata 知道它们
    # Base.metadata.create_all(bind=engine)
    # logger.info("Database table creation process completed.")

# ----------------------------------------------------
# 7. 导出核心组件
# ----------------------------------------------------

__all__ = [
    "Base",
    "SessionLocal",
    "engine",
    "init_db",
    "check_db_connection",
    "DATABASE_URL"
]