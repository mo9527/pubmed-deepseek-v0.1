from datetime import UTC, datetime, timedelta
import jwt
from app.schemas.auth_schema import JWTPayload
from app.config import CONFIG

jwt_config = CONFIG.get('jwt_config')
JWT_SECRET_KEY = jwt_config.get('secret')
JWT_ACESS_EXP = jwt_config.get('access_exp')
JWT_REFRESH_EXP = jwt_config.get('refresh_exp')


def create_access_token(*, data: JWTPayload):
    """创建访问令牌"""
    payload = data.model_dump().copy()
    # 确保token_type为access
    payload["token_type"] = "access"
    encoded_jwt = jwt.encode(
        payload, JWT_SECRET_KEY, algorithm='HS256'
    )
    
    return encoded_jwt


def create_refresh_token(user_id: int, username: str) -> str:
    """创建刷新令牌"""
    expire = datetime.now(UTC) + timedelta(seconds=JWT_REFRESH_EXP)

    payload = JWTPayload(
        user_id=user_id,
        username=username,
        exp=expire,
        token_type="refresh",
    )

    payload_dict = payload.model_dump()
    # 确保token_type为refresh
    payload_dict["token_type"] = "refresh"

    return jwt.encode(
        payload_dict, JWT_SECRET_KEY, algorithm='HS256'
    )


def verify_token(token: str, token_type: str = "access") -> JWTPayload:
    """验证令牌并返回载荷"""
    try:
        payload = jwt.decode(
            token, JWT_SECRET_KEY, algorithms=['HS256']
        )

        # 检查令牌类型
        if payload.get("token_type") != token_type:
            raise jwt.InvalidTokenError(f"Invalid token type. Expected {token_type}")

        return JWTPayload(**payload)

    except jwt.ExpiredSignatureError as e:
        raise jwt.ExpiredSignatureError("Token has expired") from e
    except jwt.InvalidTokenError as e:
        raise jwt.InvalidTokenError("Invalid token") from e


def create_token_pair(
    user_id: int, username: str
) -> tuple[str, str]:
    """创建访问令牌和刷新令牌对"""
    # 创建访问令牌
    access_expire = datetime.now(UTC) + timedelta(
        seconds=JWT_ACESS_EXP
    )
    access_payload = JWTPayload(
        user_id=user_id,
        username=username,
        exp=access_expire,
        token_type="access",
    )
    access_token = create_access_token(data=access_payload)

    # 创建刷新令牌
    refresh_token = create_refresh_token(user_id, username)

    return access_token, refresh_token
