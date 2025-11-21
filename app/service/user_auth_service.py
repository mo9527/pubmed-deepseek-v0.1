from .validate_code_service import ValidateCodeService
from .redis_service import RedisService
from .user_service import user_service
from app.util.jwt import create_token_pair
from ..schemas.auth_schema import JWTOut
from app.config import CONFIG
from ..schemas.users_schema import UserCreate


class UserAuthService:
    '''用户认证服务'''
    
    def __init__(self):
        self.jwt_config = CONFIG.get('jwt_config')
        self.JWT_ACESS_EXP = self.jwt_config.get('access_exp')
        
        self.validate_code_service = ValidateCodeService()
        self.redis_service = RedisService()
    
    async def login_sms(self, mobile:str, code:str):
        '''短信登录'''
        '''
        create new user when not exists
        update last login time
        create jwt token and refresh token paire
        '''
        await self.validate_code_service.valide_sms(mobile, code)
        user = await user_service.get_user_by_mobile(mobile)
        if user is None:
            new_user = UserCreate(mobile=mobile, 
                                  name=f'用户{mobile[6:]}', 
                                  password=None, 
                                  avatar=None,
                                  status=True,
                                  source='web',
                                  platform='web')
            user = await user_service.create_user(new_user)
            
        access_token, refresh_token = create_token_pair(user.id, user.name)
        data = JWTOut(
            access_token=access_token,
            refresh_token=refresh_token,
            username=user.name,
            expires_in=self.JWT_ACESS_EXP,
        )
        return data.model_dump()
    