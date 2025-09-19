from __future__ import annotations

import re
from datetime import datetime
from sqlalchemy import func
from app.db.db_storage import DBStorage
from app.models.order import Order
from app.models.refund import RefundRequest, RefundNotFoundLog
from app.models.email import Email, EmailImportance
from app.services.gmail_sender import send_reply
from app.core.logging_config import setup_logging


logger = setup_logging()

# Prefer well-formed IDs like ORD-XXXX or INV-XXXX, else fall back to generic token
PREFERRED_ID_REGEX = re.compile(r"\b(?:ORD|INV)-[A-Z0-9-]{3,}\b", re.IGNORECASE)
GENERIC_ID_REGEX = re.compile(r"\b[A-Z0-9-]{6,}\b", re.IGNORECASE)


def extract_order_id(subject: str | None, body: str | None) -> str | None:
    text = ((subject or "") + "\n" + (body or "")).strip()
    if not text:
        return None
    # First try preferred pattern
    m = PREFERRED_ID_REGEX.search(text)
    token = m.group(0) if m else None
    if not token:
        m2 = GENERIC_ID_REGEX.search(text)
        token = m2.group(0) if m2 else None
    if not token:
        return None
    # Trim common trailing punctuation
    token = token.strip().strip(".,;:!?)\"]}")
    return token.upper()


def process_refund_email(email_id: str) -> None:
    db = DBStorage()
    db.setup_db()
    try:
        row = db.find_by_id(Email, email_id)
        if not row:
            return

        subject_text = row.subject or ""
        message_text = (row.text_body or row.html_body or "")
        candidate_id = extract_order_id(subject_text, message_text)
        logger.info(f"Refund: extracted candidate_id={candidate_id} from subject/body for message={row.gmail_message_id}")

        if not candidate_id:
            subject = f"Re: {row.subject or ''}".strip()
            body = "Could you please provide your order ID so we can process your refund?"
            send_reply(row.account_email, row.from_email or row.account_email, subject, body, row.thread_id)
            row.handled = True
            row.importance = EmailImportance.medium
            db.update(row)
            return

        # Case-insensitive exact match against orders.order_id
        order = db.query(Order).filter(func.lower(Order.order_id) == candidate_id.lower()).first()
        logger.info(f"Refund: lookup candidate_id={candidate_id} found={bool(order)}")
        if order:
            order.refund_requested = True
            db.update(order)
            db.add(RefundRequest(thread_id=row.thread_id, order_id=candidate_id, requester_email=row.from_email))
            subject = f"Re: {row.subject or ''}".strip()
            body = "Your refund request has been received and will be processed within 3 business days."
            send_reply(row.account_email, row.from_email or row.account_email, subject, body, row.thread_id)
            row.handled = True
            row.importance = EmailImportance.low
            db.update(row)
        else:
            subject = f"Re: {row.subject or ''}".strip()
            body = "The order ID you provided appears to be invalid. Please double-check and reply with the correct order ID."
            send_reply(row.account_email, row.from_email or row.account_email, subject, body, row.thread_id)
            db.add(RefundNotFoundLog(thread_id=row.thread_id, message_id=row.gmail_message_id, provided_text=candidate_id, reason="invalid_id"))
            row.handled = False
            row.importance = EmailImportance.high
            db.update(row)
    finally:
        db.close()


