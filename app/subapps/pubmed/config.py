import yaml
import os
import sys
import re

CONFIG_FILE = 'config.yaml'
DEFAULT_ENV = 'test'
CURRENT_ENV = os.environ.get('APP_ENV', DEFAULT_ENV)

#读取当前目录下的config.yaml
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)


CONFIG = None

def load_config():
    global CONFIG
    if CONFIG:
        return CONFIG
    
    try:
        config_path = os.path.join(current_dir, CONFIG_FILE)
        print(f'pubmed app配置文件：{config_path}')
        with open(config_path, 'r', encoding='utf-8') as f:
            text = f.read()
            text = resolve_env(text)
            full_data = yaml.safe_load(text)
        
        #只取当前环境的配置，如test/prod/dev
        current_env_config = full_data.get(CURRENT_ENV)

        if current_env_config is None:
             raise ValueError(f"配置文件 '{CONFIG_FILE}' 中找不到环境 '{CURRENT_ENV}' 的配置块。")
             
        CONFIG = current_env_config
        
        print(f"配置加载成功！当前环境: {CURRENT_ENV}")
        return CONFIG
    except FileNotFoundError:
        print('配置文件未找到，程序退出')
        sys.exit(1)
    except Exception as e:
        print(f"加载配置时发生错误: {e}")
        sys.exit(1)

def resolve_env(value):
    pattern = re.compile(r'\$\{([^}^{]+)\}')
    match = pattern.findall(value)
    for m in match:
        value = value.replace(f"${{{m}}}", os.environ.get(m, ""))
    return value

load_config()


