from fastapi import APIRouter, Request, Depends, Query
from ..schemas.base_schema import R
from ..schemas.users_schema import BaseUser, UserUpdate
from ..service.user_service import user_service
from models.user_model import User

from app.core.api_limiter import apply_rate_limit
from database.db import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from ..util.model_util import ModelUtil
from dependencies.dependencies import get_current_user
from util.app_log import logger



router = APIRouter(
        prefix='/user',
        tags=['用户信息']
    )


@router.get("/get_user_info", response_model=R)
async def get_user_info(id:int = Query(description="用户ID"),
                    session: AsyncSession = Depends(get_db_session)):
    '''查询用户信息'''
    user = await user_service.get_user_by_id(session, id)
    if not user:
        return R.fail('用户不存在')
    user_schema = ModelUtil.model_to_schema(user, BaseUser)
    #user_schema.model_dump()
    logger.info(f'用户信息：{user_schema}')
    return R.success(user_schema)

@router.get("/list_users", response_model=R)
async def list_users(
    session: AsyncSession = Depends(get_db_session),
    page_num: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    name: str | None = Query(None, description="姓名"),
    mobile: str | None = Query(None, description="手机号"),
):
    '''查询用户列表'''
    page_obj = await user_service.list_users(session, page_num, page_size, name=name, mobile=mobile)
    return R.success(page_obj)

@router.post("/update_user_info", response_model=R)
async def update_user_info(
                           user:UserUpdate,
                           session: AsyncSession = Depends(get_db_session)
                        ):
    '''更新用户信息'''
    logger.info(f'更新前的用户：{user}')
    updated_user = await user_service.update_user(session, user)
    user = ModelUtil.model_to_schema(updated_user, BaseUser)
    logger.info(f'更新后的用户：{user}')
    return R.success(user)


@router.get(path = "/test_get_user_from_token", response_model=R)
async def test_get_user_from_token(current_user:dict = Depends(get_current_user)):
    return R.success(current_user)