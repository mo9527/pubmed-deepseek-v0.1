from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String
)
import datetime
from app.entity.BaseEntity import BaseEntity
from app.database.db import Base

class User(Base, BaseEntity):
    
    __tablename__ = 'user'
    
    mobile = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    avatar = Column(String(255), nullable=True)
    source = Column(String(255), nullable=True)
    platform = Column(String(255), nullable=True)
    salt = Column(String(255), nullable=True)
    status = Column(Integer, nullable=True, default=1) #0禁用1正常
    last_login = Column(DateTime, nullable=True)
    last_ip = Column(String(255), nullable=True)
    
    def __init__(self, mobile, email, name, password, source, platform):
        self.mobile = mobile
        self.email = email
        self.name = name
        self.password = password
        self.source = source
        self.platform = platform