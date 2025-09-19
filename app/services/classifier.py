from __future__ import annotations

from typing import Dict, Any
from datetime import datetime
from openai import OpenAI
from app.core.config import settings
from app.db.db_storage import DBStorage
from app.models.email import Email, EmailCategory, EmailImportance
from app.services.rag.answerer import answer_with_rag
from app.services.gmail_sender import send_reply
from app.services.refund_service import process_refund_email
from app.core.logging_config import setup_logging


client = OpenAI(api_key=settings.OPENAI_API_KEY)
logger = setup_logging()


CLASSIFIER_SYSTEM = (
    "You are an email triage assistant. Classify the user's email into one of: "
    "question, refund, other. Do not guess a refund just because an order id is present; "
    "refund requires explicit intent to request/cancel/return or similar. Output strict JSON only."
)


def classify_email(subject: str, body: str) -> Dict[str, Any]:
    prompt = {
        "subject": subject or "",
        "body": body[:6000] if body else "",
        "schema": {
            "category": "question|refund|other",
            "confidence": "0-1",
            "reason": "short rationale",
        },
    }

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": CLASSIFIER_SYSTEM},
            {"role": "user", "content": f"Classify this email. Return JSON only.\n\n{prompt}"},
        ],
        temperature=0,
    )

    content = completion.choices[0].message.content or "{}"
    import json
    try:
        data = json.loads(content)
    except Exception:
        data = {"category": "other", "confidence": 0.0, "reason": "parse_error"}
    # sanitize
    cat = str(data.get("category", "other")).lower()
    if cat not in ("question", "refund", "other"):
        cat = "other"
    conf = float(data.get("confidence", 0.0) or 0.0)
    reason = str(data.get("reason", ""))
    return {"category": cat, "confidence": conf, "reason": reason}


def classify_and_update(email_id: str) -> None:
    """Background task: load email by id, classify, and update row."""
    db = DBStorage()
    db.setup_db()
    try:
        row = db.find_by_id(Email, email_id)
        if not row:
            return
        result = classify_email(row.subject or "", row.text_body or row.html_body or "")
        # Map to enum safely
        try:
            category_enum = EmailCategory(result["category"])  # type: ignore[arg-type]
        except Exception:
            category_enum = EmailCategory.other
        row.category = category_enum
        row.confidence = result.get("confidence")
        row.reason = result.get("reason")
        row.processed_at = datetime.utcnow()
        # Other emails default to low importance
        if row.category == EmailCategory.other:
            row.importance = EmailImportance.low
        # If question, run RAG and set importance if low confidence
        if row.category == EmailCategory.question:
            rag = answer_with_rag((row.text_body or row.html_body or "")[:4000])
            rag_conf = rag.get("confidence", 0.0) or 0.0
            answer_text = rag.get("answer", "").strip()
            if rag_conf >= 0.6 and answer_text:
                # Send reply in-thread
                subject = f"Re: {row.subject or ''}".strip()
                sent_id = send_reply(
                    account_email=row.account_email,
                    to_email=row.from_email or row.account_email,
                    subject=subject,
                    body_text=answer_text,
                    thread_id=row.thread_id,
                )
                row.handled = True
                row.importance = EmailImportance.low
            else:
                # Could not confidently answer
                row.handled = False
                row.importance = EmailImportance.high
            row.reason = (row.reason or "") + f" | rag_conf={rag_conf:.2f}"
        db.update(row)

        # Refund handling
        if row.category == EmailCategory.refund:
            process_refund_email(email_id)
        logger.info(f"Classified email {row.gmail_message_id} as {row.category} (conf={row.confidence})")
    except Exception as e:
        logger.error(f"Background classification error for {email_id}: {e}")
    finally:
        db.close()


