from __future__ import annotations

import base64
from email.message import EmailMessage
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from app.core.config import settings
from app.db.db_storage import DBStorage
from app.models.gmail_account import GmailAccount


def _build_creds_for_account(account_email: str) -> Credentials | None:
    db = DBStorage()
    db.setup_db()
    try:
        acct = db.query(GmailAccount).filter(GmailAccount.user_email == account_email).first()
        if not acct or not acct.refresh_token:
            return None
        creds = Credentials(
            None,
            refresh_token=acct.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=acct.scopes.split(" ") if acct.scopes else settings.GOOGLE_OAUTH_SCOPES,
        )
        return creds
    finally:
        db.close()


def send_reply(
    account_email: str,
    to_email: str,
    subject: str,
    body_text: str,
    thread_id: str,
    in_reply_to_message_id: str | None = None,
) -> str | None:
    """Send a reply email in the same Gmail thread. Returns sent message id or None."""
    creds = _build_creds_for_account(account_email)
    if creds is None:
        return None

    msg = EmailMessage()
    msg["To"] = to_email
    msg["From"] = account_email
    msg["Subject"] = subject
    if in_reply_to_message_id:
        msg["In-Reply-To"] = in_reply_to_message_id
        msg["References"] = in_reply_to_message_id
    msg.set_content(body_text)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    gmail = build("gmail", "v1", credentials=creds)
    res = gmail.users().messages().send(
        userId="me",
        body={"raw": raw, "threadId": thread_id},
    ).execute()
    return res.get("id")


