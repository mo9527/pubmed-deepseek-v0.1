from fastapi import APIRouter
import json
import asyncio
from starlette.middleware.cors import CORSMiddleware
import os
import scripts
from app.models import R
import importlib
from app.config.config import CONFIG

api_prefix = CONFIG.get('api_prefix')
router = APIRouter(
        tags=['script_api']
    )

@router.post("/run_script/{script_name}", response_model=R)
def execute_script(script_name: str, payload: dict):
    try:
        full_script_name = f'scripts.{script_name}'
        
        script_module = importlib.import_module(full_script_name)
        if not hasattr(script_module, "main"):
            raise AttributeError(f"模块 '{script_name}' 中未找到主入口函数 'main'.")
        main_function = getattr(script_module, "main")
        execution_result = main_function(payload)
        
        return R.success(execution_result)
    except ModuleNotFoundError:
        return R.fail(f"模块 '{script_name}' 不存在.")
    except AttributeError as e:
        return R.fail(str(e))
    except Exception as e:
        return R.fail(f'脚本发生未知错误：{str(e)}')