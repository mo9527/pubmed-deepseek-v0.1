'''一些初始化工作'''
from .database.db import Base, close_connection, check_db_connection

async def db_migration():
    from db_migration import run_migrations_on_startup
    run_migrations_on_startup()
    
async def on_startup():
    await check_db_connection()
    await db_migration()

async def on_shutdown():
    await close_connection()