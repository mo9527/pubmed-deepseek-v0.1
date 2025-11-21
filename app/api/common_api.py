from fastapi import APIRouter, Request
from ..schemas.base_schema import R


router = APIRouter(
        prefix='/common',
        tags=['通用接口']
    )

@router.post("/health", response_model=R, description="健康检查")
async def health(request: Request):
    return R.success({'status': 'ok'})
