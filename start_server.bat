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

REM set envs sk-808205629ed44c8ea749042ecd3b0261
set DEEPSEEK_API_KEY=sk-808205629ed44c8ea749042ecd3b0261
set DOUBAO_API_KEY=b846f1f3-c23b-4d52-aa4a-1bac5e420488
set PUBMED_EMAIL=wanyihealife@163.com
set PUBMED_API_KEY=d2aa4ea868834376d698ac2313cf69cdd608
set APP_ENV=test

REM 启动FastAPI服务
echo [INFO] Starting Uvicorn server...
uvicorn app.main:app --host 0.0.0.0 --port 7001 --reload

pause
