@echo off
title DeepSeek PubMed Server
echo ===============================================
echo Starting DeepSeek PubMed API Server (Windows)
echo ===============================================

REM 激活虚拟环境
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo [INFO] Virtual environment activated.
) else (
    echo [WARN] Virtual environment not found. Starting without venv.
)

REM set envs
set DEEPSEEK_API_KEY=sk-e34510b96b574604a49a1b044b17e5be
set DOUBAO_API_KEY=b846f1f3-c23b-4d52-aa4a-1bac5e420488
set PUBMED_EMAIL=wanyihealife@163.com
set PUBMED_API_KEY=d2aa4ea868834376d698ac2313cf69cdd608

REM 启动FastAPI服务
echo [INFO] Starting Uvicorn server...
uvicorn app.main:app --host 0.0.0.0 --port 7001 --reload

pause
