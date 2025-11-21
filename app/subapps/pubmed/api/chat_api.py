from fastapi import FastAPI, Request, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from app.schemas.base_schema import R
from ..schemas.chat_response import QueryRequest, AnswerResponse
from ..search_engine.rag_engine import generate_answer, build_prompt, retrieve_top_articles
from ..search_engine.pubmed_client import search_pubmed
from ..search_engine.embedding import embed_text
from ..search_engine.deepseek_client import stream_deepseek, stream_reasoning
from ..search_engine.doubao_client import stream_doubao
import json
import asyncio
from app.util.app_log import logger

router = APIRouter(
        prefix='/chat',
        tags=['聊天对话']
    )


@router.get("/favicon.ico")
def favicon():
    return ""


@router.post("/ask")
def ask_question(req: QueryRequest):
    result = generate_answer(req.question)
    return R.success_data({
        "answer": result["answer"],
        "references": [
            {"pmid": a["pmid"], "title": a["title"]} for a in result["references"]
        ]
    })

@router.post("/ask/stream")
async def ask_question_stream(req: QueryRequest):
    # 搜索PubMed
    articles = search_pubmed(req.question)
    async def event_generator():
        top_articles = retrieve_top_articles(req.question, articles)
        references = json.dumps({'type': 'references', 'data': top_articles}, ensure_ascii=False)
        yield f"data: {references}\n\n"
        
        prompt = build_prompt(req.question, top_articles)
        for token in stream_deepseek(prompt):
            if token == "[DONE]":
                yield "data: [DONE]\n\n"
                break
            # 每个 token 都转为 JSON 格式发送
            chunk = json.dumps({'type': 'answer', "data": token}, ensure_ascii=False)
            yield f"data: {chunk}\n\n"
            await asyncio.sleep(0)  # 避免阻塞事件循环

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/ask/stream_reasoning")
async def ask_question_stream(req: QueryRequest):
    # 搜索PubMed
    articles = search_pubmed(req.question)
    async def event_generator():
        top_articles = retrieve_top_articles(req.question, articles)
        references = json.dumps({'type': 'references', 'data': top_articles}, ensure_ascii=False)
        yield f"data: {references}\n\n"
        
        prompt = build_prompt(req.question, top_articles)
        for token in stream_reasoning(prompt):
            data = token.get('data')
            type = token.get('type')
            if type == 'reasoning':
                chunk = json.dumps({'type': 'answer', "data": data}, ensure_ascii=False)
            elif type == 'answer':
                chunk = json.dumps({'type': 'answer', "data": data}, ensure_ascii=False)
            
            yield f"data: {chunk}\n\n"
            await asyncio.sleep(0)  # 避免阻塞事件循环

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=7001, reload=True)
