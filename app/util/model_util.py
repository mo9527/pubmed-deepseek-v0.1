
from datetime import datetime, date
from sqlalchemy import inspect

class ModelUtil:
    @staticmethod    
    def model_to_schema(model_obj, schema_cls):
        """
        将 SQLAlchemy 模型对象转换为schema。
        """
        if model_obj is None:
            return None
        return schema_cls.model_validate(model_obj)
    
    def model_to_dict(model_obj, exclude_fields=None, include_relationships=False, _visited=None, _max_depth=2):
        """
        将 SQLAlchemy 模型对象转换为字典。
        参数:
          - model_obj: SQLAlchemy ORM 实例
          - exclude_fields: 要排除的字段名列表
          - include_relationships: 是否包含关系字段（默认 False）
          - _max_depth: 递归关系的最大深度，防止循环引用（内部使用）
        返回:
          - 普通的 dict，datetime/date 自动转为 ISO 字符串
        """
        if model_obj is None:
            return None
        if exclude_fields is None:
            exclude_fields = []

        if _visited is None:
            _visited = set()

        # 防止循环引用（使用对象 id）
        obj_id = id(model_obj)
        if obj_id in _visited or _max_depth < 0:
            return None
        _visited.add(obj_id)

        data = {}
        mapper = inspect(type(model_obj))

        # 列字段
        for col in mapper.columns:
            name = col.key
            if name in exclude_fields:
                continue
            val = getattr(model_obj, name)
            if isinstance(val, (datetime, date)):
                val = int(val.timestamp())
            data[name] = val

        # 可选：关系字段
        if include_relationships:
            for rel in mapper.relationships:
                name = rel.key
                if name in exclude_fields:
                    continue
                try:
                    related = getattr(model_obj, name)
                except Exception:
                    related = None
                if related is None:
                    data[name] = None
                else:
                    # 多值关系（列表/集合）
                    if rel.uselist:
                        items = []
                        for item in related:
                            item_dict = ModelUtil.model_to_dict(item, exclude_fields=exclude_fields,
                                                                 include_relationships=False,
                                                                 _visited=_visited,
                                                                 _max_depth=_max_depth - 1)
                            items.append(item_dict)
                        data[name] = items
                    else:
                        data[name] = ModelUtil.model_to_dict(related, exclude_fields=exclude_fields,
                                                             include_relationships=False,
                                                             _visited=_visited,
                                                             _max_depth=_max_depth - 1)
        return data
        
    def models_to_list(model_objs: list, schema_cls=None, exclude_fields=None, include_relationships=False, _max_depth=2):
        """
        将多个 SQLAlchemy 模型对象转换为列表。
        参数:
          - model_objs: SQLAlchemy ORM 实例列表
          - schema_cls: 可选的 Pydantic schema 类（若提供则使用 schema 转换）
          - exclude_fields: 要排除的字段名列表
          - include_relationships: 是否包含关系字段
          - _max_depth: 递归关系的最大深度
        返回:
          - 普通的 list（每项为 dict 或 schema 实例）
        """
        if not model_objs:
            return []

        if exclude_fields is None:
            exclude_fields = []

        result = []
        for obj in model_objs:
            if obj is None:
                result.append(None)
                continue

            if schema_cls:
                # 使用 schema 进行转换（pydantic v2: model_validate）
                try:
                    result.append(schema_cls.model_validate(obj))
                except Exception:
                    # fallback: convert to dict if schema validation fails
                    result.append(ModelUtil.model_to_dict(obj, exclude_fields=exclude_fields,
                                                         include_relationships=include_relationships,
                                                         _visited=set(),
                                                         _max_depth=_max_depth))
            else:
                result.append(ModelUtil.model_to_dict(obj, exclude_fields=exclude_fields,
                                                     include_relationships=include_relationships,
                                                     _visited=set(),
                                                     _max_depth=_max_depth))
        return result
        
        
