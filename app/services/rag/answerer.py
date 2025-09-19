from __future__ import annotations

import json
from typing import Dict, Any, List
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.schema import Document
from app.services.rag.vectorstore_provider import get_vectorstore
from app.core.config import settings


def retrieve_context(query: str, k: int = 4) -> List[Document]:
    vs = get_vectorstore()
    retriever = vs.as_retriever(search_kwargs={"k": k})
    return retriever.get_relevant_documents(query)


def answer_with_rag(question: str) -> Dict[str, Any]:
    docs = retrieve_context(question, k=4)
    context = "\n\n".join([d.page_content for d in docs])

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=settings.OPENAI_API_KEY)
    system = (
        "You are a helpful support assistant for Numeo AI. Answer using ONLY the context. "
        "If the answer is not in context, say you don't have enough information. After the answer, "
        "provide a numeric confidence between 0 and 1 as JSON."
    )
    user = (
        f"Context:\n{context}\n\nQuestion:\n{question}\n\n"
        "Respond in JSON with keys: answer (string), confidence (0..1)."
    )
    resp = llm.invoke([
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ])
    try:
        data = json.loads(resp.content)
    except Exception:
        data = {"answer": "", "confidence": 0.0}
    return {"answer": data.get("answer", ""), "confidence": float(data.get("confidence", 0.0)), "sources": docs}


