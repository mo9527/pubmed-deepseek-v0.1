from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from models import QueryRequest, AnswerResponse
from rag_engine import generate_answer
from rag_engine import build_prompt
from rag_engine import retrieve_top_articles
from pubmed_client import search_pubmed
from embedding import embed_text
from deepseek_client import stream_deepseek
from doubao_client import stream_doubao
import json
import asyncio
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(title="DeepSeek-PubMed Demo")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
