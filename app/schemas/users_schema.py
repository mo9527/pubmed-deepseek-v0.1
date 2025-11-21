import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class BaseUser(BaseModel):
    id: int
    mobile: str = Field(..., description="手机号", example="13112345678", min_length=11, max_length=11)
    email: EmailStr | None = Field(description="邮箱", example="admin@qq.com", min_length=5, max_length=30)
    name: str | None = Field(description="用户名", example="admin", min_length=2, max_length=30)
    status: bool | None = True
    platform: str | None = False
    source: str | None = Field(description="注册来源", example="web")
    avatar: str | None = Field(description="头像URL", example="https://example.com/avatar.jpg")
    created_at: datetime | None
    updated_at: datetime | None
    last_login: datetime | None
    last_ip: str | None
    ext_1: str | None
    ext_2: str | None
    ext_3: str | None
    ext_4: str | None
    ext_5: str | None


class UserCreate(BaseModel):
    mobile: str = Field(example="13112341234")
    name: str = Field(
        example="admin",
        min_length=2,
        max_length=20,
        description="用户名（2-20位字母数字下划线）",
    )
    password: str|None = Field(description="密码（至少6位，包含字母和数字）")
    status: bool | None = True
    source: str | None = None
    platform: str | None = None
    avatar: str | None = None
    last_login: datetime | None = None
    

    # @field_validator("password")
    # def validate_password_strength(cls, v):
    #     """验证密码强度"""
    #     if len(v) < 6:
    #         raise ValueError("密码长度至少6位")

    #     if not re.search(r"[A-Za-z]", v):
    #         raise ValueError("密码必须包含字母")

    #     if not re.search(r"\d", v):
    #         raise ValueError("密码必须包含数字")

        # 可选：检查特殊字符
        # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
        #     raise ValueError('密码建议包含特殊字符')

        # return v

    @field_validator("name")
    def validate_username(cls, value):
        """验证用户名格式"""
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

    # def create_dict(self):
    #     return self.model_dump(exclude_unset=True, exclude={"role_ids"})


class UserUpdate(BaseModel):
    id: int
    name: str
    status: bool | None = True
    avatar: str | None
    platform: str | None = False
    source: str | None = None
    ext_1: str | None
    ext_2: str | None
    ext_3: str | None
    ext_4: str | None
    ext_5: str | None


class UpdatePassword(BaseModel):
    old_password: str = Field(description="旧密码")
    new_password: str = Field(
        min_length=6, description="新密码（至少6位，包含字母和数字）"
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password_strength(cls, v):
        """验证新密码强度"""
        if len(v) < 6:
            raise ValueError("新密码长度至少6位")

        if not re.search(r"[A-Za-z]", v):
            raise ValueError("新密码必须包含字母")

        if not re.search(r"\d", v):
            raise ValueError("新密码必须包含数字")

        return v
