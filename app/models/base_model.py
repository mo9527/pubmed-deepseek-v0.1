from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String,
)
import datetime
from app.database.db import Base

class BaseModel:
    """model的基类,所有model都必须继承"""
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    update_by = Column(String(255), nullable=True)
    create_by = Column(String(255), nullable=True)
    deleted_at = Column(DateTime, nullable=True)  # 可以为空, 如果非空, 则为软删
    deleted_flag = Column(Integer, default=0)