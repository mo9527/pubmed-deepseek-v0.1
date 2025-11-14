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

app = FastAPI(title="DeepSeek-PubMed Demo")

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


@app.post("/ask", response_model=AnswerResponse)
def ask_question(req: QueryRequest):
    result = generate_answer(req.question)
    return {
        "answer": result["answer"],
        "references": [
            {"pmid": a["pmid"], "title": a["title"]} for a in result["references"]
        ]
    }

@app.post("/ask/stream")
async def ask_question_stream(req: QueryRequest):
    # 搜索PubMed
    articles = search_pubmed(req.question)
    
    async def event_generator():
        top_articles = retrieve_top_articles(req.question, articles)
        references = json.dumps({'type': 'references', 'data': top_articles}, ensure_ascii=False)
        yield f"data: {references}\n\n"
        
        prompt = build_prompt(req.question, top_articles)
        for token in stream_doubao(prompt):
            if token == "[DONE]":
                yield "data: [DONE]\n\n"
                break
            # 每个 token 都转为 JSON 格式发送
            chunk = json.dumps({'type': 'answer', "data": token}, ensure_ascii=False)
            yield f"data: {chunk}\n\n"
            await asyncio.sleep(0)  # 避免阻塞事件循环

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=7001, reload=True)
