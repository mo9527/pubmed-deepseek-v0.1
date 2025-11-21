from fastapi import FastAPI, APIRouter
import sys
from pathlib import Path
import importlib
from app.util.app_log import logger



API_DIR = 'api'
API_PACKAGE_NAME = f'app.subapps.pubmed.{API_DIR}' #api目录完整包名

print(f'API_PACKAGE_NAME: {API_PACKAGE_NAME}')

def create_app() -> FastAPI:
    app = FastAPI(title="DeepSeek-PubMed", root_path="/api/v1/pubmed")

    def register_routers(app: FastAPI):
        api_dir_path = Path(__file__).parent / API_DIR
        logger.info(f"Pubmed 子项目开始自动注册路由...")
        for file_path in api_dir_path.glob("*.py"):
            if file_path.name == "__init__.py":
                continue
            module_name = f"{API_PACKAGE_NAME}.{file_path.stem}"
            print(f'module_name: {module_name}')
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
    return app

pubmed_app = create_app()


__all__ = ["pubmed_app"]