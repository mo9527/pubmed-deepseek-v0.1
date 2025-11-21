#程序入口
from app.util.app_log import logger
from fastapi import FastAPI, Request, APIRouter
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
import os
from pathlib import Path
from app.init_app import on_startup, on_shutdown

from .subapps.pubmed import pubmed_app

import sys
import importlib
from contextlib import asynccontextmanager
from slowapi.errors import RateLimitExceeded
from app.core.exceptions import (
    AuthException,
    AuthExcHandle,
    NotFoundException,
    DoesNotExistHandle,
    HTTPException,
    HttpExcHandle,
    IntegrityError,
    IntegrityHandle,
    RequestValidationError,
    RequestValidationHandle,
    ResponseValidationError,
    ResponseValidationHandle,
    RateLimitHandle,
    GlobalExcHandle,
)

from middleware.JWTAuthMiddleware import JWTAuthMiddleware



API_DIR = 'api'
API_PACKAGE_NAME = f'app.{API_DIR}'

ROOT_PATH = "/api/v1"

# origins = ["*"]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"]
# )
# app.add_middleware(JWTAuthMiddleware)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await on_startup()
    yield
    await on_shutdown()

def make_middlewares():
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        ),
        Middleware(
            JWTAuthMiddleware,
            methods=["GET", "POST", "PUT", "DELETE"],
            exclude_paths=[
                f"{ROOT_PATH}/docs",
                f"{ROOT_PATH}/redoc",
                f"{ROOT_PATH}/openapi.json",
                "*/common/health",
                "*/auth/send_sms/*",
                "*/auth/login_sms",
                "*/auth/register",
                "*/static/*",
                "*/favicon.ico",
                "*/pubmed/*" #临时测试用
            ]
        )
    ]
    return middleware

app = FastAPI(title="DeepSeek-PubMed",
              root_path=ROOT_PATH, 
              middleware=make_middlewares(),
              lifespan=lifespan
            )

current_dir = os.path.dirname(os.path.abspath(__file__))
static_files_dir = os.path.join(current_dir, "..", "static")
app.mount(
    "/static", 
    StaticFiles(directory=static_files_dir, html=True), 
    name="static"
)

def register_exceptions(app: FastAPI):
        app.add_exception_handler(Exception, GlobalExcHandle)
        app.add_exception_handler(AuthException, AuthExcHandle)
        app.add_exception_handler(NotFoundException, DoesNotExistHandle)
        app.add_exception_handler(HTTPException, HttpExcHandle)
        app.add_exception_handler(IntegrityError, IntegrityHandle)
        app.add_exception_handler(RequestValidationError, RequestValidationHandle)
        app.add_exception_handler(ResponseValidationError, ResponseValidationHandle)
        # 注册限流异常处理
        app.add_exception_handler(RateLimitExceeded, RateLimitHandle)
        
def register_routers(app: FastAPI):
        api_dir_path = Path(__file__).parent / API_DIR
        logger.info(f"Pubmed 子项目开始自动注册路由...")
        for file_path in api_dir_path.glob("*.py"):
            if file_path.name == "__init__.py":
                continue
            module_name = f"{API_PACKAGE_NAME}.{file_path.stem}"
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, "router") and isinstance(getattr(module, "router"), APIRouter):
                        router_instance = getattr(module, "router")
                        app.include_router(router_instance)
                        logger.info(f"成功注册路由: {module_name} (Prefix: {router_instance.prefix})")
                else:
                    logger.info(f"模块 {module_name} 已导入，但未找到名为 'router' 的 APIRouter 实例。")
            except ImportError as e:
                logger.error(f"无法导入模块 {module_name}: {e}", stack_info=True)
                sys.exit(1)
            except Exception as e:
                logger.error(f"注册模块 {module_name} 时发生未知错误: {e}", stack_info=True)
                sys.exit(1)

        logger.info(" pubmed路由自动注册完成。")
        

register_routers(app)   
register_exceptions(app)

def mount_sub_apps(app: FastAPI):
    '''挂载子应用'''
    app.mount("/pubmed", pubmed_app )

mount_sub_apps(app)

# @app.on_event("startup")
# def on_startup():
#     '''db migration'''
#     from db_migration import run_migrations_on_startup
#     run_migrations_on_startup()


__all__ = ["app"]


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=7001, reload=True)
