from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

def apply_rate_limit(rate="5/minute"):
    """根据环境应用限流装饰器"""

    def decorator(func):
        import os
        app_env = os.getenv("APP_ENV", "test").lower()

        # if app_env == "test" or app_env == "dev":
        #     return func  # 测试开发环境不限流
        return limiter.limit(limit_value=rate, error_message="Too many requests")(func)

    return decorator