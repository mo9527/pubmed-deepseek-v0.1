import requests
import os
import json

DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY")
DOUBAO_API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
MODE_ID = 'deepseek-v3-1-250821'

def ask_doubao(prompt: str):
    """普通非流式调用"""
    payload = {
        "model": MODE_ID,
        "messages": [{"role": "user", "content": prompt}]
    }
    headers = {"Authorization": f"Bearer {DOUBAO_API_KEY}"}
    response = requests.post(DOUBAO_API_URL, json=payload, headers=headers, timeout=60)
    res_json = response.json()
    if res_json.get('error'):
        print('deepseek返回错误：', res_json)
        return None
    return response.json()["choices"][0]["message"]["content"]

def stream_doubao(prompt: str):
    """流式调用，逐块返回"""
    payload = {
        "model": MODE_ID,
        "messages": [
            {"role": "system", "content": '你是一个科学论文助手，根据 PubMed 数据回答问题，结果以MarkDown格式输出。'},
            {"role": "user", "content": prompt}
            ],
        "stream": True
    }
    headers = {"Authorization": f"Bearer {DOUBAO_API_KEY}"}
    with requests.post(DOUBAO_API_URL, json=payload, headers=headers, stream=True) as resp:
        for line in resp.iter_lines():
            if not line or line.strip() == "":
                continue
            
            data = line.decode('utf-8')
            
            data = data[len("data:"):].strip()
            if data == "[DONE]":
                yield "[DONE]"
            else:
                try:
                    chunk = json.loads(data)
                    delta = chunk["choices"][0]["delta"]
                    if "content" in delta:
                        yield delta["content"]
                except Exception as e:
                    print(e)
                    continue
