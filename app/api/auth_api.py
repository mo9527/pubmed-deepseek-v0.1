from fastapi import APIRouter, Request
import json
import asyncio
from starlette.middleware.cors import CORSMiddleware
import os
import scripts
from ..schemas.base_schema import R
import importlib
from ..service.user_auth_service import UserAuthService

from app.util.sms_provider import send_zt_sms, gen_code
from ..schemas.auth_schema import CredentialsSms
from ..service.validate_code_service import ValidateCodeService
from app.core.api_limiter import apply_rate_limit


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
    return R.success()

@router.post("/login_sms", response_model=R)
@apply_rate_limit()
async def login_sms(request: Request, req: CredentialsSms):
    '''短信登录'''
    res = await user_auth_service.login_sms(req.mobile, req.code)
    return R.success_data(res)