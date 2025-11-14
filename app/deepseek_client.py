import requests
import os
import json

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def ask_deepseek(prompt: str):
    """普通非流式调用"""
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=60)
    res_json = response.json()
    if res_json.get('error'):
        print('deepseek返回错误：', res_json)
        return None
    return response.json()["choices"][0]["message"]["content"]

def stream_deepseek(prompt: str):
    """流式调用，逐块返回"""
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "stream": True
    }
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    with requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, stream=True) as resp:
        for line in resp.iter_lines(decode_unicode = True):
            if not line or line.strip() == "":
                continue
            if not line.startswith("data:"):
                continue
            data = line[len("data:"):].strip()
            
            data = data.decode("utf-8")
            if data.strip() == "[DONE]":
                yield "[DONE]"
            else:
                try:
                    chunk = json.loads(data)
                    delta = chunk["choices"][0]["delta"]
                    if "content" in delta:
                        yield delta["content"]
                except Exception:
                    continue
