from models.user_model import User
from fastapi import Depends
from ..schemas.users_schema import BaseUser, UserCreate, UserUpdate
from ..repositories.user_repo import user_repository
from app.util.app_log import logger
from datetime import datetime
from database.db import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from util.model_util import ModelUtil
from schemas.base_schema import Page



class UserService:
    '''用户服务'''
    
    def __init__(self):
        pass
        
    
    async def create_user(self, session: AsyncSession, user:UserCreate):
        '''创建用户'''
        logger.info(f'创建用户：{user}')
        existed_user = await self.get_user_by_mobile(session, user.mobile)
        if existed_user:
            raise Exception('用户已存在')
        if not user.name:
            user.name = f'用户{user.mobile[:6]}'
        user.last_login = datetime.now()
        user = await user_repository.create_user(session, user)
        return user
    
    async def list_users(self, session: AsyncSession, page_num:int = 1, page_size:int = 10, **kwargs):
        '''查询用户列表'''
        name = kwargs.get('name')
        mobile = kwargs.get('mobile')
        where = None
        if mobile:
            where = User.mobile == mobile
        if name:
            #like
            where = User.name.ilike(f'%{name}%')
            
        if where:
            total, users = await user_repository.page(session, page_num, page_size, where)
        else:
            total, users = await user_repository.page(session, page_num, page_size)
        return Page(total=total, page_num=page_num, page_size=page_size, items=ModelUtil.models_to_list(users, BaseUser))
    
    async def update_user(self, session: AsyncSession, user:UserUpdate):
        '''更新用户'''
        assert user.id is not None, '用户ID不能为空'
        updated_user = await user_repository.update(session, user.id, user)
        return updated_user
        
    
    async def get_user_by_mobile(self, session: AsyncSession, mobile:str):
        '''通过手机号获取用户'''
        user = await user_repository.get_by_mobile(session, mobile)
        return user
    
    async def get_user_by_id(self, session: AsyncSession, user_id:int) -> User | None:
        '''获取用户'''
        user = await user_repository.get(session, user_id)
        return user
    
    async def update_last_login(self, session: AsyncSession, user_id:int):
        '''更新用户最后登录时间'''
        await user_repository.update_last_login(session, user_id)
        
        
user_service = UserService()
        
    