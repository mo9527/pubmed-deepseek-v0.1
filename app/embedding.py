from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import app.config as config
import os

model_path = config.BGE_M3_MODEL_PATH
model_name = config.BGE_M3_MODEL_NAME
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
