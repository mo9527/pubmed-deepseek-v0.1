from app.util.sms_provider import send_zt_sms, gen_code
from ..service.redis_service import RedisService
from app.util.app_log import logger
from app.core.exceptions import AuthException
from ..constants.redis_key import KEY_SMS_CODE



class ValidateCodeService:
    '''验证码服务'''

    def __init__(self):
        self.redis_service = RedisService()
    
    async def send_sms(self, mobile:str):
        '''
        发送短信
        发送短信前，需校验时间间隔以及当日总共的发送次数不大于阈值
        '''
        code = gen_code(6)
        logger.info(f'{mobile} 验证码：{code}')
        send_zt_sms(mobile, code)
        self.redis_service.set(KEY_SMS_CODE.format(mobile = mobile), code, 600) #验证码10分钟有效
        
    
    async def valide_sms(self, mobile:str, code:str):
        '''验证短信'''
        cache_key = KEY_SMS_CODE.format(mobile = mobile)
        if not self.redis_service.exists(cache_key):
            logger.debug(f'验证码已过期：{mobile} : {code}')
            raise AuthException('验证码已过期')
        cache_code = str(self.redis_service.get(cache_key))
            
        if cache_code == code:
            logger.debug(f'{mobile} 验证码正确：{mobile} : {code}')
            self.redis_service.delete(cache_key)
        else:
            logger.debug(f'{mobile} 验证码错误：{mobile} : {code}, cache_code: {cache_code}')
            raise AuthException('验证码错误')
        
    def send_email(self, email:str):
        '''发送邮件'''
        pass
        
    def valide_email(self, email:str, code:str):
        '''验证邮件'''
        pass