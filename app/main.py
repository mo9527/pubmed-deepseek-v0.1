from fastapi import FastAPI, Request, APIRouter
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from app.models import QueryRequest, AnswerResponse
from app.rag_engine import generate_answer, build_prompt, retrieve_top_articles
from app.pubmed_client import search_pubmed
from app.embedding import embed_text
from app.deepseek_client import stream_deepseek
from app.doubao_client import stream_doubao
import json
import asyncio
from starlette.middleware.cors import CORSMiddleware
import os
import app.api.chat_api as chat_api
from pathlib import Path
import importlib.util
from app.app_log import logger

API_DIR = 'api'
API_PACKAGE_NAME = API_DIR

@asynccontextmanager
async def lifespan(app: FastAPI):
    on_startup()
    yield

app = FastAPI(title="DeepSeek-PubMed", root_path="/api/v1")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

current_dir = os.path.dirname(os.path.abspath(__file__))
static_files_dir = os.path.join(current_dir, "..", "static")
app.mount(
    "/static", 
    StaticFiles(directory=static_files_dir, html=True), 
    name="static",
)

def register_routers(app: FastAPI):
    api_dir_path = Path(__file__).parent / API_DIR
    logger.info(f"开始自动注册路由...")
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
            logger.error(f"无法导入模块 {module_name}: {e}")
            continue
        except Exception as e:
            logger.error(f"注册模块 {module_name} 时发生未知错误: {e}")
        
    
    logger.info("路由自动注册完成。")
app.include_router(chat_api.router)

async def on_startup():
    pass


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=7001, reload=True)
