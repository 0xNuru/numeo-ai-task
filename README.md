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

## OAuth & Gmail Watch (ngrok + Pub/Sub)

1. ngrok (HTTPS for local OAuth callbacks)

```bash
ngrok http http://localhost:8000
# Copy the HTTPS forwarding URL, e.g. https://<subdomain>.ngrok-free.app
```

Update `GOOGLE_REDIRECT_URI` in `.env` and Google Console to:

```
https://<your-ngrok-subdomain>.ngrok-free.app/auth/google/callback
```

2. Required env vars in `.env` (see `app/core/config.py`)

```
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=https://<your-ngrok-subdomain>.ngrok-free.app/auth/google/callback
GCP_PROJECT_ID=your-gcp-project-id
GMAIL_PUBSUB_TOPIC=projects/your-gcp-project-id/topics/gmail-push
```

3. Google Cloud Console setup

- Enable Gmail API and Cloud Pub/Sub APIs
- Create Pub/Sub topic (e.g., `gmail-push`)
- Create a PUSH subscription with endpoint:
  `https://<your-ngrok-subdomain>.ngrok-free.app/webhook/gmail-push`
- In Gmail `users.watch` calls, we use labels from `GMAIL_WATCH_LABEL_IDS` (defaults to `INBOX`).

4. Scopes used

- `gmail.readonly`, `gmail.send`

5. Start OAuth

```bash
open http://localhost:8000/auth/google
```

You can also start auth by clicking connect Gmail from UI.

Next sections:

- Email ingestion and classification
- RAG answering
- Refund flow.
