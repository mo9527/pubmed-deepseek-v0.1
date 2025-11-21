from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from starlette.responses import Response
from sqlalchemy.exc import IntegrityError
from slowapi.errors import RateLimitExceeded
from app.config import CONFIG

log_level = CONFIG.get('log_level')

class SettingNotFound(Exception):
    pass
class NotFoundException(HTTPException):
    def __init__(self, msg = '资源未找到'):
        super().__init__(status_code=200, detail=msg)
        
class AuthException(HTTPException):
    def __init__(self, msg):
        super().__init__(status_code=200, detail=msg)


async def AuthExcHandle(req: Request, exc: HTTPException):
    if log_level.upper() == 'DEBUG':
        msg = f"Not authenticated: {exc}, query_params: {req.query_params}"
    else:
        msg = "未授权的访问"

    content = dict(code=401, msg=msg)
    return JSONResponse(content=content, status_code=200)

async def DoesNotExistHandle(req: Request, exc: HTTPException) -> JSONResponse:
    # 根据环境决定错误信息详细程度
    if log_level.upper() == 'DEBUG':
        msg = f"Object not found: {exc}, query_params: {req.query_params}"
    else:
        msg = "请求的资源不存在"

    content = dict(code=404, msg=msg)
    return JSONResponse(content=content, status_code=200)


async def HttpExcHandle(request: Request, exc: HTTPException):
    if exc.status_code == 401 and exc.headers and "WWW-Authenticate" in exc.headers:
        return Response(status_code=exc.status_code, headers=exc.headers)
    return JSONResponse(
        status_code=200,
        content={"code": exc.status_code, "msg": exc.detail, "data": None},
    )


async def IntegrityHandle(request: Request, exc: IntegrityError):
    # 根据环境决定错误信息详细程度
    if log_level.upper() == 'DEBUG':
        msg = f"IntegrityError: {exc}"
    else:
        msg = "数据完整性错误，请检查输入数据"

    content = dict(code=500, msg=msg)
    return JSONResponse(content=content, status_code=200)


async def RequestValidationHandle(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    # 根据环境决定错误信息详细程度
    if log_level.upper() == 'DEBUG':
        msg = f"RequestValidationError: {exc}"
    else:
        msg = "请求参数验证失败，请检查输入格式"

    content = dict(code=422, msg=msg)
    return JSONResponse(content=content, status_code=200)


async def ResponseValidationHandle(
    _: Request, exc: ResponseValidationError
) -> JSONResponse:
    # 根据环境决定错误信息详细程度
    if log_level.upper() == 'DEBUG':
        msg = f"ResponseValidationError: {exc}"
    else:
        msg = "服务器响应格式错误"

    content = dict(code=500, msg=msg)
    return JSONResponse(content=content, status_code=200)

async def GlobalExcHandle(request: Request, exc: Exception):
    if log_level.upper() == 'DEBUG':
        msg = f"Unknow Exception: {exc}"
    else:
        msg = "服务器内部错误"

    content = dict(code=500, msg=msg)
    return JSONResponse(content=content, status_code=200)


async def RateLimitHandle(request: Request, exc: RateLimitExceeded):
    content = dict(code=429, msg="请求过于频繁，请稍后再试")
    return JSONResponse(content=content, status_code=200)