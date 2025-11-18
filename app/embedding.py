from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
from app.config.config import CONFIG
import os

model_path = CONFIG.get('bge_m3_model').get('path')
model_name = CONFIG.get('bge_m3_model').get('name')
# model_path = "D:/bge-m3"
# model_name = "BAAI/bge-m3"

if not model_path or  os.path.exists(model_path) == False:
    #离线model不存在，则使用model name
    model_path = model_name

model = SentenceTransformer(model_path)

def embed_text(texts: Union[str, List[str]]):
    """
    为单个或多个文本生成嵌入向量。
    """
    return model.encode(texts, normalize_embeddings=True)
