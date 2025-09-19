from __future__ import annotations

from pathlib import Path
from typing import List
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_markdown_directory(dir_path: str | Path) -> List[str]:
    """Load all markdown/txt files from a directory into raw strings."""
    dir_path = str(dir_path)
    loader = DirectoryLoader(dir_path, glob="**/*", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
    docs = loader.load()
    return [d.page_content for d in docs]


def split_documents(texts: List[str], chunk_size: int = 1000, chunk_overlap: int = 150) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks: List[str] = []
    for t in texts:
        chunks.extend(splitter.split_text(t))
    return chunks


