from fastapi import Header, HTTPException, status, Request, Depends
from util.jwt import verify_token
from typing import Optional

def get_current_user(request: Request) -> dict:
    """
    取出已存储的用户数据。
    """
    user_data = getattr(request.state, "current_user", None)
    if user_data is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User data missing from state.")
    
    return user_data