# Numeo AI – Customer Support Email Agent

This repository implements a customer support email agent with:

- Gmail OAuth connect/disconnect (supports multiple accounts)
- Real-time email ingestion via Gmail Push + Pub/Sub
- LLM-based categorization (question/refund/other)
- RAG answers for questions (pgvector + LangChain)
- Refund workflow with order lookups and reply automation

## Minimal Web UI

Screenshot:
![Web UI Screenshot](static/web-ui.png)

How to run locally in dev:

```bash
uv run uvicorn main:app --reload
# Browse http://localhost:8000/
```

Next sections:

- Gmail OAuth & Watch
- Email ingestion and classification
- RAG answering
- Refund flow
