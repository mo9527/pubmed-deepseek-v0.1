from models.user_model import User
from ..schemas.users_schema import BaseUser, UserCreate, UserUpdate
from ..repositories.user_repo import user_repository
from app.util.app_log import logger
from datetime import datetime

class UserService:
    '''用户服务'''
    
    def __init__(self):
        pass
    
    async def create_user(self, user:UserCreate):
        '''创建用户'''
        logger.info(f'创建用户：{user}')
        existed_user = await self.get_user_by_mobile(user.mobile)
        if existed_user:
            raise Exception('用户已存在')
        if not user.name:
            user.name = f'用户{user.mobile[:6]}'
        user.last_login = datetime.now()
        user = await user_repository.create_user(user)
        return user
        
    
    async def update_user(self, user:UserUpdate):
        '''更新用户'''
        pass
    
    async def get_user_by_mobile(self, mobile:str):
        '''通过手机号获取用户'''
        user = await user_repository.get_by_mobile(mobile)
        return user
    
    async def get_user_by_id(self,user_id:int):
        '''获取用户'''
        user = await user_repository.get(user_id)
        return user
    
    async def update_last_login(self, user_id:int):
        '''更新用户最后登录时间'''
        await user_repository.update_last_login(user_id)
        
        
user_service = UserService()
        
    