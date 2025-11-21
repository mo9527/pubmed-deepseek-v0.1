import numpy as np
from .embedding import embed_text
from .pubmed_client import search_pubmed
from .deepseek_client import ask_deepseek

def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def retrieve_top_articles(question: str, articles: list, top_k: int = 10) -> list:
    """
    计算问题和文献列表相关度
    """
    if not articles:
        return []
    article_texts = [f"{art['title']} {art['abstract']}" for art in articles]
    q_vec, *article_vecs = embed_text([question] + article_texts)

    scores = [cosine_sim(q_vec, a_vec) for a_vec in article_vecs]
    scored = sorted(zip(scores, articles), reverse=True, key=lambda x: x[0])
    return [art for _, art in scored[:top_k]]

def build_prompt(question, articles):
    context = []
    for i, art in enumerate(articles, 1):
        context.append(f"[{i}] PMID: {art['pmid']}\nTitle: {art['title']}\nAbstract: {art['abstract']}")
    prompt = f"""
            用户问题：{question}
            以下是相关的 PubMed 文献摘要：
            {chr(10).join(context)}
            请你基于以上文献，用严谨的学术语气回答用户问题。
            在回答中引用文献时请使用 [ref:数字] 标注引用。
            以中文输出结果。
        """
    return prompt

def generate_answer(question):
    articles = search_pubmed(question)
    top_articles = retrieve_top_articles(question, articles)
    prompt = build_prompt(question, top_articles)
    answer = ask_deepseek(prompt)
    return {"answer": answer, "references": top_articles}
