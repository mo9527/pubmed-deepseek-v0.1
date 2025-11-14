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

REM 设置环境变量（你可替换自己的Key）
set DEEPSEEK_API_KEY=your_api_key_here

REM 启动FastAPI服务
echo [INFO] Starting Uvicorn server...
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
