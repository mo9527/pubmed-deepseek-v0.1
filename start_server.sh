#!/bin/bash
if ! command -v uvicorn >/dev/null 2>&1; then
  echo "uvicorn not found, installing..."
  pip install uvicorn fastapi > /dev/null
fi

if [ -f "requirements.txt" ]; then
  echo "install project dependencies..."
  pip install -r requirements.txt
fi

echo "Start PubMed+DeepSeek API service..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 7001 --reload
