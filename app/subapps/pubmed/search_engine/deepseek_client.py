import requests
import os
import json
from openai import OpenAI


DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL_NAME = "deepseek-reasoner"

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def ask_deepseek(prompt: str):
    """普通非流式调用"""
    payload = {
        "model": MODEL_NAME,
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
        "model": MODEL_NAME,
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

REASONING_MODEL = "deepseek-reasoner"
def stream_reasoning(prompt: str, pre_content:str = None):
    '''
      Params: 
        prompt: 用户提问
        pre_content: 上一轮ai回答
    '''
    messages = [
        {"role": "system", "content": '你是一个科学论文助手，根据 PubMed 数据回答问题，结果以MarkDown格式输出。'},
        {"role": "user",  "content": prompt}
    ]
    if pre_content:
        messages.append({"role": "assistant", "content": pre_content})
    
    response = client.chat.completions.create(
        model=REASONING_MODEL,
        messages=messages,
        stream=True
    )
    
    for chunk in response:
        if chunk.choices[0].delta.reasoning_content:
            reasoning_chunk = chunk.choices[0].delta.reasoning_content
            if not reasoning_chunk:
                continue
            yield {"type": "reasoning", "data": reasoning_chunk}
        else:
            content_chunk = chunk.choices[0].delta.content
            if not content_chunk:
                continue
            yield {"type": "answer", "data": content_chunk}
            

