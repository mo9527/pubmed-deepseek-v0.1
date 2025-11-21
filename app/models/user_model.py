from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String,
    Boolean
)
from sqlalchemy.orm import validates
from .base_model import BaseModel
from app.database.db import Base
import re

class User(Base, BaseModel):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True, autoincrement=True)      # 主键
    mobile = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    avatar = Column(String(255), nullable=True)
    source = Column(String(255), nullable=True)
    platform = Column(String(255), nullable=True)
    salt = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=False, default=True) #0禁用1正常
    last_login = Column(DateTime, nullable=True)
    last_ip = Column(String(255), nullable=True)
    
    ext_1 = Column(String(255), nullable=True)
    ext_2 = Column(String(255), nullable=True)
    ext_3 = Column(String(255), nullable=True)
    ext_4 = Column(String(255), nullable=True)
    ext_5 = Column(String(255), nullable=True)
    
    
    @validates('mobile')
    def validate_mobile(self, key, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise ValueError("invalid mobile number")
        return value
    
    # @validates('email')
    # def validate_email(self, key, value):
    #     if '@' not in value:
    #         raise ValueError("invalid email address")
    #     return value
    
    # @validates('password')
    # def validate_password(self, key, value):
    #     if len(value) < 6:
    #         raise ValueError("password must be at least 6 characters long")
    #     if not re.search(r"[A-Za-z]", value):
    #         raise ValueError("password must contain letters")

    #     if not re.search(r"\d", value):
    #         raise ValueError("password must contain digits")
    #     return value
    
    @validates('name')
    def validate_name(self, key, value):
        if not value or len(value) < 2:
            raise ValueError("name must be at least 2 characters long")
        # 只允许字母数字、空白、下划线、连字符、点、中文字符和中点
        allowed_punct = {'-', '_', '.', '·'}
        for ch in value:
            if ch.isalnum():
                continue
            if ch in allowed_punct:
                continue
            code = ord(ch)
            # 常用汉字
            if 0x4E00 <= code <= 0x9FFF:
                continue
            raise ValueError("name contains invalid characters")
        return value