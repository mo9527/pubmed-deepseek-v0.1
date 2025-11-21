'''一些初始化工作'''
from .database.db import Base, close_connection

async def db_migration():
    from db_migration import run_migrations_on_startup
    run_migrations_on_startup()
    
async def on_startup():
    await db_migration()

async def on_shutdown():
    close_connection()