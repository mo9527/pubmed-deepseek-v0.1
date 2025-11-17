from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from app.models import QueryRequest, AnswerResponse
from app.rag_engine import generate_answer, build_prompt, retrieve_top_articles
from app.pubmed_client import search_pubmed
from app.embedding import embed_text
from app.deepseek_client import stream_deepseek
from app.doubao_client import stream_doubao
import json
import asyncio
from starlette.middleware.cors import CORSMiddleware
import os
import app.api.main_api as main_api


app = FastAPI(title="DeepSeek-PubMed")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

current_dir = os.path.dirname(os.path.abspath(__file__))
static_files_dir = os.path.join(current_dir, "..", "static")
app.mount(
    "/static", 
    StaticFiles(directory=static_files_dir, html=True), 
    name="static"
)

app.include_router(main_api.router)


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=7001, reload=True)
