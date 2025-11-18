# app_logger.py
import logging
import logging.handlers
import os
import sys

# 从您的配置单例模块中导入配置
# 假设 config.py 已经成功加载了当前环境的配置到 CONFIG 变量
try:
    from app.config.config import CONFIG, CURRENT_ENV 
except ImportError:
    print("错误：无法从 config 模块导入配置。请确保 config.py 运行正常。")
    sys.exit(1)

# --- 定义日志配置 ---
# 确保日志级别和路径是可用的，否则使用默认值
LOG_LEVEL_STR = CONFIG.get('log_level', 'INFO').upper()
LOG_PATH = CONFIG.get('log_path', 'logs')
LOG_FILENAME = CONFIG.get('log_filename', 'app.log')

# 将日志级别字符串转换为 logging 模块的常量
LOG_LEVEL = getattr(logging, LOG_LEVEL_STR, logging.INFO)

# 日志格式
LOG_FORMAT = '%(asctime)s - %(levelname)s - [%(name)s] - %(filename)s:%(lineno)d - %(message)s'

def setup_logging(logger_name: str = 'root_app_logger'):
    """
    配置并返回一个具有每日归档和控制台输出的 Logger 实例。
    """
    # 1. 确保日志目录存在
    os.makedirs(LOG_PATH, exist_ok=True)
    
    # 2. 创建 Logger 实例
    logger = logging.getLogger(logger_name)
    logger.setLevel(LOG_LEVEL)
    
    # 避免重复添加 Handler
    if logger.hasHandlers():
        return logger

    # 3. 定义 Formatter
    formatter = logging.Formatter(LOG_FORMAT)

    # --- Handler 1: TimedRotatingFileHandler (每日归档) ---
    log_file_path = os.path.join(LOG_PATH, LOG_FILENAME)
    
    # when='midnight'：每天午夜滚动一次
    # interval=1：每隔 1 天
    # backupCount=7：保留最近 7 天的归档文件
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_file_path,
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # --- Handler 2: StreamHandler (控制台输出) ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    print(f"[日志初始化] 环境: {CURRENT_ENV}, 级别: {LOG_LEVEL_STR}, 路径: {log_file_path}")
    
    return logger

# 模块导入时，自动配置并获取根 Logger 实例
# 其他文件只需 from app_logger import logger 即可使用
logger = setup_logging()

# 此外，如果需要处理第三方库的日志，可以配置根 Logger
logging.basicConfig(level=LOG_LEVEL, handlers=[]) # 清除默认配置
logging.getLogger().setLevel(LOG_LEVEL) # 设置根 Logger 级别，以控制第三方库的日志输出