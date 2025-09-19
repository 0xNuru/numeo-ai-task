from __future__ import annotations

from pathlib import Path
from typing import List
from app.services.rag.loaders import load_markdown_directory, split_documents
from app.services.rag.vectorstore_provider import get_vectorstore


def ingest_directory(dir_path: str | Path) -> int:
    texts = load_markdown_directory(dir_path)
    chunks = split_documents(texts)
    if not chunks:
        return 0
    vs = get_vectorstore()
    vs.add_texts(chunks)
    return len(chunks)


