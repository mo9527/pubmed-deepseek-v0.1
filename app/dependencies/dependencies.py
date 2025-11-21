from fastapi import Header, HTTPException, status, Request, Depends
from util.jwt import verify_token
from typing import Optional

async def authenticate(request: Request, authorization: Optional[str] = Header(None)):
    """
    执行鉴权，并将用户数据存储到请求状态中。
    """
    if authorization is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing")
    
    scheme, token = authorization.split() if ' ' in authorization else ('', authorization)
    if scheme.lower() != 'bearer' or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication scheme.")

    try:
        user_payload = verify_token(token)
        request.state.current_user = user_payload
        return user_payload 
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {e}")

def get_current_user(request: Request) -> dict:
    """
    取出已存储的用户数据。
    """
    user_data = getattr(request.state, "current_user", None)
    if user_data is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User data missing from state.")
    
    return user_data