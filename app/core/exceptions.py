from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from starlette.responses import Response
from sqlalchemy.exc import IntegrityError
from slowapi.errors import RateLimitExceeded
from app.config import CONFIG
from util.app_log import logger
from functools import wraps
import asyncio


log_level = CONFIG.get('log_level')

# class SettingNotFound(Exception):
#     pass
# class NotFoundException(HTTPException):
#     def __init__(self, msg = '资源未找到'):
#         super().__init__(status_code=200, detail="资源未找到")

def log_request_params():
    #定义一个wrapper,用于打印请求路径和参数，从request中提取
    """
    装饰器：在调用 handler 前记录请求方法、路径、query params 及可解析的 body（尽量获取 JSON 或文本）。
    适用于 async 和 sync handler（FastAPI 的 exception handler 为 async）。
    用法：
        @log_request_params()
        async def MyHandler(request: Request, exc: Exception): ...
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(req: Request, *args, **kwargs):
            try:
                qp = dict(req.query_params)
                body = None
                try:
                    body = await req.json()
                except Exception:
                    try:
                        raw = await req.body()
                        body = raw.decode('utf-8') if raw else None
                    except Exception:
                        body = None
                logger.debug(f"Request -> method={req.method} path={req.url.path}， query_params={qp} body={body}")
            except Exception as _e:
                logger.debug(f"log_request_params failed: {_e}")
            return await func(req, *args, **kwargs)

        @wraps(func)
        def sync_wrapper(req: Request, *args, **kwargs):
            try:
                qp = dict(req.query_params)
                logger.debug(f"Request -> method={req.method} path={req.url.path}， query_params={qp}")
            except Exception as _e:
                logger.debug(f"log_request_params failed (sync): {_e}")
            return func(req, *args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator

        
class AuthException(HTTPException):
    def __init__(self, msg = '未授权的访问'):
        super().__init__(status_code=200, detail="未授权的访问")


@log_request_params()
async def AuthExcHandle(req: Request, exc: HTTPException):
    logger.debug(f'请求路径: {req.url.path}')
    if log_level.upper() == 'DEBUG':
        msg = f"Not authenticated: {exc}, query_params: {req.query_params}"
    else:
        msg = "未授权的访问"

    content = dict(code=401, msg=msg)
    return JSONResponse(content=content, status_code=200)

@log_request_params()
async def NotFoundHandle(req: Request, exc: HTTPException) -> JSONResponse:
    logger.debug(f'请求路径: {req.url.path}')
    # 根据环境决定错误信息详细程度
    if log_level.upper() == 'DEBUG':
        msg = f"Object not found: {exc}, query_params: {req.query_params}"
    else:
        msg = "请求的资源不存在"

    content = dict(code=404, msg=msg)
    return JSONResponse(content=content, status_code=200)


@log_request_params()
async def HttpExcHandle(req: Request, exc: HTTPException):
    logger.debug(f'请求路径: {req.url.path}')
    if exc.status_code == 401 and exc.headers and "WWW-Authenticate" in exc.headers:
        return Response(status_code=exc.status_code, headers=exc.headers)
    if exc.status_code == 404:
        return JSONResponse(
            status_code=200,
            content={"code": exc.status_code, "msg": "请求的资源不存在.", "data": None}
        )
    return JSONResponse(
        status_code=200,
        content={"code": exc.status_code, "msg": exc.detail, "data": None},
    )

@log_request_params()
async def IntegrityHandle(req: Request, exc: IntegrityError):
    logger.debug(f'请求路径: {req.url.path}')
    # 根据环境决定错误信息详细程度
    if log_level.upper() == 'DEBUG':
        msg = f"IntegrityError: {exc}"
    else:
        msg = "数据完整性错误，请检查输入数据"

    content = dict(code=500, msg=msg)
    return JSONResponse(content=content, status_code=200)

@log_request_params()
async def RequestValidationHandle(
    req: Request, exc: RequestValidationError
) -> JSONResponse:
    # 根据环境决定错误信息详细程度
    logger.debug(f'请求路径: {req.url.path}')
    if log_level.upper() == 'DEBUG':
        msg = f"RequestValidationError: {exc}"
    else:
        msg = "请求参数验证失败，请检查输入格式"

    content = dict(code=422, msg=msg)
    return JSONResponse(content=content, status_code=200)

@log_request_params()
async def ResponseValidationHandle(
    req: Request, exc: ResponseValidationError
) -> JSONResponse:
    # 根据环境决定错误信息详细程度
    logger.debug(f'请求路径: {req.url.path}')
    if log_level.upper() == 'DEBUG':
        msg = f"ResponseValidationError: {exc}"
    else:
        msg = "服务器响应格式错误"

    content = dict(code=500, msg=msg)
    return JSONResponse(content=content, status_code=200)

@log_request_params()
async def GlobalExcHandle(req: Request, exc: Exception):
    logger.debug(f'请求路径: {req.url.path}')
    if log_level.upper() == 'DEBUG':
        msg = f"Unknow Exception: {exc}"
    else:
        msg = "服务器内部错误"

    content = dict(code=500, msg=msg)
    return JSONResponse(content=content, status_code=200)


@log_request_params()
async def RateLimitHandle(req: Request, exc: RateLimitExceeded):
    logger.debug(f'请求路径: {req.url.path}')
    content = dict(code=429, msg="请求过于频繁，请稍后再试")
    return JSONResponse(content=content, status_code=200)