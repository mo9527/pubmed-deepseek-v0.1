from fastapi import APIRouter, Request, Depends
from ..schemas.base_schema import R
from ..service.user_auth_service import UserAuthService

from app.util.sms_provider import send_zt_sms, gen_code
from ..schemas.auth_schema import CredentialsSms
from ..service.validate_code_service import ValidateCodeService
from app.core.api_limiter import apply_rate_limit
from database.db import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession



router = APIRouter(
        prefix='/auth',
        tags=['用户认证']
    )

user_auth_service = UserAuthService()
validate_code_service = ValidateCodeService()


@router.post("/send_sms/{mobile}", response_model=R)
@apply_rate_limit("1/minute")
async def send_sms(request: Request, mobile:str):
    await validate_code_service.send_sms(mobile)
    return R.success_empty()

@router.post("/login_sms", response_model=R)
@apply_rate_limit()
async def login_sms(request: Request, req: CredentialsSms, session: AsyncSession = Depends(get_db_session)):
    '''短信登录'''
    res = await user_auth_service.login_sms(session, req.mobile, req.code)
    return R.success(res)