from pydantic import BaseModel, Field, ConfigDict, field_serializer
from typing import Any, Optional, TypeVar, Type, Generic, Sequence
from datetime import datetime

RType = TypeVar('RType', bound='R')

class R(BaseModel):
    data: Optional[Any] = Field(default=None, description="业务数据")
    msg: str = Field(default="操作成功", description="状态信息")
    code: int = Field(default=200, description="业务状态码")

    @classmethod
    def of(cls: Type[RType], code: int = 200, msg: str = "操作成功", data: Optional[Any] = None) -> RType:
        """
        创建任意自定义状态的响应
        """
        return cls(code=code, msg=msg, data=data)

    @classmethod
    def success(cls: Type[RType], data: Optional[Any] = None, msg: str = "操作成功") -> RType:
        return cls(code=200, data=data, msg=msg)

    @classmethod
    def success_empty(cls: Type[RType], msg: str = "操作成功") -> RType:
        return cls(code=200, data=None, msg=msg)
    
    @classmethod
    def fail(cls: Type[RType], msg: str = "操作失败", code: int = 500) -> RType:
        return cls(code=code, msg=msg, data=None)

T = TypeVar("T")
class Page(BaseModel, Generic[T]):
    total: int
    page_num: int
    page_size: int
    items: Sequence[T]
    
class BaseSchema(BaseModel):
    model_config = ConfigDict(
        # 启用 ORM 模式
        from_attributes=True,
    )
    
    @field_serializer('*', when_used='always')
    def serialize_datetime_to_timestamp(self, value: Any, info) -> Any:
        """
        如果字段是 datetime 对象，则转换为时间戳。
        """
        if isinstance(value, datetime):
            # 将 datetime 对象转换为整数时间戳（秒级）
            # 必须使用 int() 确保输出是整数而不是浮点数
            return int(value.timestamp())
        
        # 否则，返回原始值
        return value