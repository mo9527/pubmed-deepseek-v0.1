from typing import Any, Generic, TypeVar, NewType, Sequence, Iterable, Type
from pydantic import BaseModel
from sqlalchemy import select, update as sql_update, delete as sql_delete, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy.exc import NoResultFound

# 假设 ModelType 绑定到 SQLAlchemy Base
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
Total = NewType("Total", int)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    基于 SQLAlchemy 2.0 异步 API 的通用 CRUD 基础类。
    
    Session 必须通过方法参数注入（例如从 FastAPI Depends 传入）。
    """
    def __init__(self, model: type[ModelType]):
        self.model = model
    
    async def get(self, db: AsyncSession, id: int) -> ModelType | None:
        """根据 ID 获取单个对象。"""
        result: Result = await db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    # ---分页查询 (PAGE) ---
    async def page(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        where: Any = None,
        order: list | None = None,
        *,
        search_fields: Iterable[str] | None = None,
        search_keyword: str | None = None
    ) -> tuple[Total, Sequence[ModelType]]:
        '''分页查询'''
        
        # 1. 构造基础查询语句
        stmt = select(self.model)

        # --- 2. 过滤条件 (模糊和普通) ---
        if search_fields and search_keyword:
            like = f"%{search_keyword}%"
            fuzzy_conditions = []

            for field in search_fields:
                col = getattr(self.model, field, None)
                if col is not None:
                    fuzzy_conditions.append(col.ilike(like))

            if fuzzy_conditions:
                fuzzy_expr = or_(*fuzzy_conditions)
                stmt = stmt.where(fuzzy_expr)

        if where is not None:
            stmt = stmt.where(where)

        # 3. 排序
        if order:
            stmt = stmt.order_by(*order)

        # 4. --- 计数查询 (核心修改点：异步和应用过滤条件) ---
        # 必须对已经应用了 WHERE 条件的查询进行计数
        count_stmt = select(func.count()).select_from(stmt.subquery())
        
        # 异步执行计数
        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()

        # 5. 分页限制和执行
        if page < 1:
            page = 1
            
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        
        # 异步执行数据查询
        result: Result = await db.execute(stmt)

        # 使用 .scalars().all() 获取 ORM 对象列表
        return Total(total), result.scalars().all()
    
    # --- 3. 不分页查询 (LIST) ---
    async def list(
        self,
        db: AsyncSession, # ⬅️ Session 必须作为参数传入
        where: Any = None,
        order: list | None = None,
        *,
        search_fields: Iterable[str] | None = None,
        search_keyword: str | None = None
    ) -> Sequence[ModelType]:
        '''不分页查询'''
        total, result = await self.page(
                                db, # 传入 db session
                                page=1,
                                page_size=1_000_000, # 足够大的数实现不分页
                                where=where,
                                order=order,
                                search_fields=search_fields,
                                search_keyword=search_keyword
                             )

        return result

    # --- 4. 创建对象 (CREATE) ---
    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        """创建单个对象并提交。"""
        if isinstance(obj_in, dict):
            obj_dict = obj_in
        else:
            obj_dict = obj_in.model_dump()

        obj = self.model(**obj_dict)
        
        # 异步 Session 的操作：add
        db.add(obj)
        
        # 异步 Session 的操作：await commit 和 await refresh
        await db.commit()
        await db.refresh(obj) # 刷新对象以获取数据库生成的 ID 等值
        
        return obj

    # --- 5. 更新对象 (UPDATE) ---
    async def update(self, db: AsyncSession, id: int, obj_in: UpdateSchemaType | dict[str, Any]) -> ModelType:
        """根据 ID 更新对象。"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            # 排除未设置和 ID 字段
            update_data = obj_in.model_dump(exclude_unset=True, exclude={"id"})

        if not update_data:
            # 如果没有更新数据，直接返回现有对象
            existing_obj = await self.get(db, id)
            if existing_obj is None:
                raise NoResultFound(f"User with id {id} not found.")
            return existing_obj
        
        stmt = (
            sql_update(self.model)
            .where(self.model.id == id)
            .values(**update_data)
        )
        
        # 异步执行更新语句
        await db.execute(stmt)
        
        # 提交事务
        await db.commit()
        
        # 刷新并返回更新后的对象
        return await self.get(db, id)

    async def remove(self, db: AsyncSession, id: int) -> None:
        """根据 ID 删除对象。"""
        stmt = sql_delete(self.model).where(self.model.id == id)
        await db.execute(stmt)
        await db.commit()