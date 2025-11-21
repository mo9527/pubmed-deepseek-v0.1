from pydantic import BaseModel, Field
from datetime import datetime


class CredentialsSms(BaseModel):
    mobile: str = Field(..., description="手机号", example="13112345678", min_length=11, max_length=11)
    code: str = Field(..., description="验证码", example="123456")
    
class JWTOut(BaseModel):
    access_token: str
    refresh_token: str
    username: str
    token_type: str = "bearer"
    expires_in: int  # 过期时间（秒）


class JWTPayload(BaseModel):
    user_id: int
    username: str
    exp: datetime
    token_type: str = "access"  # access 或 refresh


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="刷新令牌")


class TokenRefreshOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # 新access_token过期时间（秒）