from typing import Any, Generic, TypeVar, NewType, Sequence, Iterable
from pydantic import BaseModel
from sqlalchemy import select, update as sql_update, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_
from ..database.db import SessionLocal

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
Total = NewType("Total", int)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]):
        self.model = model
        self.session = SessionLocal()

    async def get(self, id: int) -> ModelType | None:
        result = self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def page(
        self,
        session: AsyncSession,
        page: int = 1,
        page_size: int = 10,
        where: Any = None,
        order: list | None = None,
        *,
        search_fields: Iterable[str] | None = None,
        search_keyword: str | None = None
    ) -> tuple[Total, Sequence[ModelType]]:
        '''分页查询'''
        stmt = select(self.model)

        # --- 多字段模糊查询 ---
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

        # 普通 where
        if where is not None:
            stmt = stmt.where(where)

        # 排序
        if order:
            stmt = stmt.order_by(*order)

        # count
        count_stmt = stmt.with_only_columns(self.model.id)
        total_result = await session.execute(count_stmt)
        total = len(total_result.scalars().all())

        # 分页
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await session.execute(stmt)

        return Total(total), result.scalars().all()
    
    
    async def list(
        self,
        session: AsyncSession,
        where: Any = None,
        order: list | None = None,
        *,
        search_fields: Iterable[str] | None = None,
        search_keyword: str | None = None
    ):
        '''不分页查询'''
        total, result = await self.page(
                            session,
                            page=1,
                            page_size=10000,
                            where=where,
                            order=order,
                            search_fields=search_fields,
                            search_keyword=search_keyword
                        )

        return result

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        if isinstance(obj_in, dict):
            obj_dict = obj_in
        else:
            obj_dict = obj_in.model_dump()

        print(obj_dict)
        obj = self.model(**obj_dict)
        with self.session as s:
            s.add(obj)
            s.commit()
            s.refresh(obj)
            return obj

    async def update(self, session: AsyncSession, id: int, obj_in: UpdateSchemaType | dict[str, Any]) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True, exclude={"id"})

        stmt = (
            sql_update(self.model)
            .where(self.model.id == id)
            .values(**update_data)
            .execution_options(synchronize_session="fetch")
        )
        await session.execute(stmt)
        await session.flush()

        return await self.get(session, id)

    async def remove(self, session: AsyncSession, id: int) -> None:
        stmt = sql_delete(self.model).where(self.model.id == id)
        await session.execute(stmt)
        await session.flush()
