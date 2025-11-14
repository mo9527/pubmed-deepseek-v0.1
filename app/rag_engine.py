import numpy as np
from embedding import embed_text
from pubmed_client import search_pubmed
from deepseek_client import ask_deepseek

def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def retrieve_top_articles(question, articles, top_k=10):
    q_vec = embed_text(question)
    scored = []
    for art in articles:
        text = f"{art['title']} {art['abstract']}"
        a_vec = embed_text(text)
        score = cosine_sim(q_vec, a_vec)
        scored.append((score, art))
    scored.sort(reverse=True, key=lambda x: x[0])
    return [a for _, a in scored[:top_k]]

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
            回答结束后请列出引用文献列表（包含PMID和标题）。
        """
    return prompt

def generate_answer(question):
    articles = search_pubmed(question)
    top_articles = retrieve_top_articles(question, articles)
    prompt = build_prompt(question, top_articles)
    answer = ask_deepseek(prompt)
    return {"answer": answer, "references": top_articles}
