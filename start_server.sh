#!/bin/bash
if ! command -v uvicorn >/dev/null 2>&1; then
  echo "uvicorn not found, installing..."
  pip install uvicorn fastapi > /dev/null
fi

echo "Start PubMed+DeepSeek API service..."

#set envs sk-808205629ed44c8ea749042ecd3b0261
export DEEPSEEK_API_KEY='sk-e34510b96b574604a49a1b044b17e5be'
export DOUBAO_API_KEY='b846f1f3-c23b-4d52-aa4a-1bac5e420488'
export PUBMED_EMAIL='wanyihealife@163.com'
export PUBMED_API_KEY='d2aa4ea868834376d698ac2313cf69cdd608'

python3 -m uvicorn app.main:app --host 0.0.0.0 --port 7001 --reload
