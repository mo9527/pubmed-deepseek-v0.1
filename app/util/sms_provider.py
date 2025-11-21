import requests
import json
import random
from ..config import CONFIG
from app.util.app_log import logger
from datetime import datetime
import hashlib

sms_config = CONFIG.get('sms_config')
url = sms_config.get('url')
username = sms_config.get('username')
password = sms_config.get('password')
product_id = sms_config.get('productId')

hl = hashlib.md5()
CODE_TEMPLETE = '您的验证码是：{code}，请不要告诉任何人，10分钟内有效，如非本人操作请忽略本短信【医助宝】。'
RAW_TEMPLETE = '{raw_content}，退订回N【医助宝】。'

def send_zt_sms(mobile, code):
    content = CODE_TEMPLETE.format(code=code)
    now = datetime.now()
    tKey = now.strftime("%Y%m%d%H%M%S")
    
    hl.update((password).encode(encoding='utf-8'))
    pwd_sign = hl.hexdigest()
    hl.update((pwd_sign + tKey).encode(encoding='utf-8'))
    password_sign = hl.hexdigest()
    
    body = {
        "username": username,
        "password": password_sign,
        "tkey": tKey,
        "mobile": mobile,
        "content": content,
        "product_id": product_id,
        "xh": ""
    }
    logger.info(f'Zt发送短信：{body}')
    res = requests.post(url=url, json=body)
    
    if res.status_code == 200:
        logger.info(f'Zt短信发送结果: {res.text}')
    else:
        logger.error(f'Zt短信发送失败: {res.text}')


def gen_code(len:int = 6):
    '''生成验证码'''
    code = ''
    for _ in range(len):
        code += str(random.randint(0, 9))
    return code
        

if __name__ == '__main__':
    send_zt_sms('18501635120', '998430')