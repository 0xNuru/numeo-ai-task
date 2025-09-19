from __future__ import annotations

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.pgvector import PGVector
from app.core.config import settings


def get_pg_engine_url() -> str:
    return (
        f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )


def get_vectorstore(collection_name: str = "numeo_kb") -> PGVector:
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=settings.OPENAI_API_KEY)
    vs = PGVector(
        connection_string=get_pg_engine_url(),
        collection_name=collection_name,
        embedding_function=embeddings,
    )
    return vs


