from fastapi import Header, HTTPException, status, Request, Depends
from util.jwt import verify_token
from typing import Optional

# ----------------- 核心鉴权逻辑 -----------------
async def authenticate(request: Request, authorization: Optional[str] = Header(None)):
    """
    执行鉴权，并将用户数据存储到请求状态中。
    这个函数会被添加到 Router 的全局依赖中。
    """
    # ... (您的 JWT 校验和解析逻辑，与之前相同) ...
    if authorization is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing")
    
    scheme, token = authorization.split() if ' ' in authorization else ('', authorization)
    if scheme.lower() != 'bearer' or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication scheme.")

    try:
        user_payload = verify_token(token)
        
        # !!! 关键步骤：将用户数据存储到请求状态中 !!!
        # 注意：Starlette/FastAPI 的请求状态可以通过 request.state 访问
        request.state.current_user = user_payload
        
        # 依赖项必须返回一个值，这里返回 None 或 user_payload 都可以，但我们主要目的是副作用
        return user_payload 
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {e}")

# ----------------- 简化的数据获取依赖 -----------------
def get_current_user(request: Request) -> dict:
    """
    从请求状态中取出已存储的用户数据。
    这个函数会被用在路由参数中。
    """
    # 鉴权已经在 authenticate_and_store_user 中完成，这里只需要安全地获取数据
    user_data = getattr(request.state, "current_user", None)
    
    # 虽然理论上全局依赖保证了数据存在，但为了健壮性，可以再检查一次
    if user_data is None:
        # 如果代码逻辑没问题，这行代码永远不会被执行
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User data missing from state.")
    
    return user_data