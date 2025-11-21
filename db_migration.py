import subprocess
import sys
import os
import time

ALEMBIC_CONFIG = 'alembic.ini'

def run_migrations_on_startup(max_retries=3, delay=5):
    """
    应用启动时，自动运行 Alembic 升级到最新版本。
    适用于容器化/自动化部署环境。
    """
    print("--------------------------------------------------")
    print("启动数据库迁移")
    print("--------------------------------------------------")
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    alembic_ini_path = os.path.join(project_root, ALEMBIC_CONFIG)
    
    print(f'alembic.ini路径：{alembic_ini_path}')
    
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                ["alembic", "-c", alembic_ini_path, "upgrade", "head"],
                check=True,
                capture_output=True, # 捕获输出
                text=True
            )
            
            print(result.stdout)
            print("Alembic 迁移成功！")
            return True

        except subprocess.CalledProcessError as e:
            print(f"迁移失败 (尝试 {attempt + 1}/{max_retries})：Alembic 命令执行失败。")
            # 可能是数据库服务尚未完全启动
            print(f"错误信息: {e.stdout}")
            print(f"错误信息: {e.stderr}")
            if attempt < max_retries - 1:
                print(f"等待 {delay} 秒后重试...")
                time.sleep(delay)
            else:
                print("致命错误：数据库迁移多次失败，应用无法启动。")
                sys.exit(1)
        except FileNotFoundError:
            print("致命错误：无法找到 Alembic 命令或 alembic.ini。请检查安装和路径。")
            sys.exit(1)
            
    return False

if __name__ == '__main__':
    run_migrations_on_startup()