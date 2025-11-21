# auth_middleware.py

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp
from util.jwt import verify_token
from schemas.base_schema import R
from core.ctx import CTX_USER_ID
import fnmatch
from util.app_log import logger


class JWTAuthMiddleware(BaseHTTPMiddleware):
    '''JWT鉴权中间件'''
    
    def __init__(self, app: ASGIApp, methods: list[str], exclude_paths: list[str]):
        super().__init__(app)
        self.free_paths = exclude_paths

    async def dispatch(self, request: Request, call_next):
        path = request.scope.get('path', '')
        
        # 路径含有 /open
        is_open_path = "/open" in path 
        # 白名单检查
        is_free_path = self.in_white_path(path, self.free_paths)
        #文档路径
        is_docs_path = '/docs' in path or '/redoc' in path
        
        if is_open_path or is_free_path or is_docs_path:
            # 放行
            return await call_next(request)

        # 校验token
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            r = R.fail("Authentication required.", code=401)
            logger.warning("没有未携带token")
            return JSONResponse(content=r.model_dump())

        try:
            token = auth_header.split(" ")[1]
            user_payload = verify_token(token) 
            
            CTX_USER_ID.set(user_payload.user_id)
            # 存储用户数据到请求的 scope/state ，state是一个dict
            request.state.current_user = user_payload.model_dump()
        except Exception as e:
            r = R.fail("Invalid token.", code=401)
            logger.warning("无效的token")
            return JSONResponse(content=r)

        return await call_next(request)
    
    def in_white_path(self, path:str, white_paths:list[str]) -> bool:
        normalized_path = path.rstrip('/')
        for pattern in white_paths:
            if fnmatch.fnmatch(normalized_path, pattern):
                print(f'白名单路径匹配：{path}')
                return True
        return False