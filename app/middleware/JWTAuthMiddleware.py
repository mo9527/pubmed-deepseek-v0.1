# auth_middleware.py

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp
from util.jwt import verify_token
from schemas.response import R
import fnmatch
from util.app_log import logger



# 假设这个是需要放行的路径列表（不包含 /open 的情况）
FREE_PATHS = [
    "/api/v1/login", 
    "/api/v1/health" # 自定义放行接口
]

class JWTAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, methods: list[str], exclude_paths: list[str]):
        super().__init__(app)
        self.free_paths = exclude_paths

    async def dispatch(self, request: Request, call_next):
        # 1. 获取完整的请求路径
        path = request.scope.get('path', '')
        
        # 2. 检查放行条件
        # 路径以 /open 开头的放行
        is_open_path = "/open" in path 
        # 白名单检查
        is_free_path = self.in_white_path(path, self.free_paths)
        #文档路径
        is_docs_path = '/docs' in path or '/redoc' in path
        
        
        if is_open_path or is_free_path or is_docs_path:
            # 放行，不执行鉴权逻辑
            return await call_next(request)

        # 3. 鉴权逻辑
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            r = R.fail_msg_code(401, "Authentication required.")
            logger.warning("没有未携带token")
            return JSONResponse(content=r.model_dump())

        try:
            token = auth_header.split(" ")[1]
            # 假设 verify_jwt_token 是您的校验函数
            user_payload = verify_token(token) 
            
            # 4. 存储用户数据到请求的 scope/state (关键!)
            # 存到 state 可以在 Request/Response 生命周期内访问
            request.state.current_user = user_payload.model_dump()
            
        except Exception as e:
            r = R.fail_msg_code(401, "Invalid token.")
            logger.warning("无效的token")
            return JSONResponse(content=r)

        # 5. 鉴权通过，请求继续
        return await call_next(request)
    
    def in_white_path(self, path:str, white_paths:list[str]) -> bool:
        normalized_path = path.rstrip('/')
        print(f'path: {path}, white_paths: {white_paths}')
        for pattern in white_paths:
            if fnmatch.fnmatch(normalized_path, pattern):
                print(f'白名单路径匹配：{path}')
                return True
        return False