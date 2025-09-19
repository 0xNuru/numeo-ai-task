from __future__ import annotations

from pathlib import Path
from app.services.rag.ingest import ingest_directory


def main():
    kb_dir = Path("knowledge/docs")
    count = ingest_directory(kb_dir)
    print(f"Ingested {count} chunks from {kb_dir}")


if __name__ == "__main__":
    main()


