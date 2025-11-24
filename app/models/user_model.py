from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String,
    Boolean,
    ForeignKey
)
from sqlalchemy.orm import validates
from .base_model import BaseModel
from app.database.db import Base
import re

class User(Base, BaseModel):
    '''用户表'''
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True, autoincrement=True)      # 主键
    mobile = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    avatar = Column(String(255), nullable=True)
    source = Column(String(255), nullable=True, comment='注册来源web/app/h5')
    platform = Column(String(255), nullable=True, comment='平台web/app/h5')
    salt = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=False, default=True, comment='0禁用1正常') 
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
    
class UserCertification(Base, BaseModel):
    '''用户认证信息表'''
    __tablename__ = 'user_certification'
    id = Column(Integer, primary_key=True, autoincrement=True)      # 主键
    name = Column(String(255), nullable=False, comment='姓名')
    user_id = Column(Integer, nullable=False)
    
    id_type = Column(Integer, nullable=False, default='身份证/医师资格证', comment='证件类型')
    id_card_number = Column(String(255), nullable=False, comment="证件号码")
    id_card_image_front = Column(String(255), nullable=True, comment="证件正面图片链接")
    id_card_image_back = Column(String(255), nullable=True, comment="证件背面图片链接")

    proof_files = Column(String(500), nullable=True, comment="证明材料图片链接，逗号分隔")
    status = Column(Integer, nullable=False, default=1, comment='认证状态0无效1有效')
    submit_time = Column(DateTime, nullable=True, comment='提交时间')
    audit_status = Column(Integer, nullable=True, default=0, comment='审核状态0未审核1审核通过2审核不通过')
    audit_time = Column(DateTime, nullable=True, comment='审核时间')
    audit_user_id = Column(Integer, nullable=True, comment='审核人ID')
    audit_user_name = Column(String(255), nullable=True, comment='审核人姓名')
    audit_remark = Column(String(255), nullable=True, comment='审核备注')
    audit_source = Column(String(255), nullable=True, comment='认证来源web/app/h5')
    
    ext_1 = Column(String(255), nullable=True)
    ext_2 = Column(String(255), nullable=True)
    ext_3 = Column(String(255), nullable=True)
    ext_4 = Column(String(255), nullable=True)
    ext_5 = Column(String(255), nullable=True) 
    
    
class UserCertificationHistory(UserCertification):
    '''用户认证历史信息表，继承UserCertification的全部信息'''
    __tablename__ = 'user_certification_history'
    id = Column(Integer, primary_key=True, autoincrement=True)      # 主键
    certification_id = Column(Integer, ForeignKey('user_certification.id'), nullable=False, comment='认证ID')
    
    