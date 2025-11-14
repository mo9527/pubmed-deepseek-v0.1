from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("BAAI/bge-m3")

def embed_text(text: str):
    return model.encode(text, normalize_embeddings=True)
