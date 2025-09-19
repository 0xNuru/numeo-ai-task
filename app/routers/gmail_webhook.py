from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
import base64
import json
from app.db.load import load
from app.models.gmail_account import GmailAccount
from app.core.config import settings
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from app.core.logging_config import setup_logging
from app.services.gmail_processing import parse_message_full
from app.models.email import Email, EmailDirection
from app.services.classifier import classify_and_update



webhook = APIRouter(prefix="/webhook", tags=["gmail-webhook"])
logger = setup_logging()


@webhook.post("/gmail-push")
async def gmail_push(request: Request, db=Depends(load), background_tasks: BackgroundTasks = None):
    body = await request.json()
    message = body.get("message", {})
    data_b64 = message.get("data")
    if not data_b64:
        return JSONResponse({"ok": True})

    try:
        decoded = base64.b64decode(data_b64).decode("utf-8")
        payload = json.loads(decoded)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid PubSub payload")

    email_address = payload.get("emailAddress")
    history_id = payload.get("historyId")
    if not email_address or not history_id:
        return JSONResponse({"ok": True})

    acct = db.query(GmailAccount).filter(GmailAccount.user_email == email_address).first()
    if not acct or not acct.refresh_token:
        return JSONResponse({"ok": True})

    creds = Credentials(
        None,
        refresh_token=acct.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=acct.scopes.split(" ") if acct.scopes else settings.GOOGLE_OAUTH_SCOPES,
    )

    gmail = build("gmail", "v1", credentials=creds)

    start_history_id = acct.last_history_id or history_id
    try:
        history_res = (
            gmail.users()
            .history()
            .list(userId="me", startHistoryId=start_history_id, historyTypes=["messageAdded"], maxResults=50)
            .execute()
        )

        messages_to_fetch = []
        for h in history_res.get("history", []):
            for added in h.get("messagesAdded", []):
                msg = added.get("message")
                if msg and msg.get("id"):
                    messages_to_fetch.append(msg["id"])

        for msg_id in messages_to_fetch:
            msg = gmail.users().messages().get(userId="me", id=msg_id, format="full").execute()
            parsed = parse_message_full(msg)
            label_ids = msg.get("labelIds", []) or []
            from_header = (parsed.get("from") or "").lower()
            is_outbound = ("SENT" in label_ids) or (email_address.lower() in from_header)
            direction_val = EmailDirection.outbound if is_outbound else EmailDirection.inbound

            # Upsert email by gmail_message_id
            existing = db.query(Email).filter(Email.gmail_message_id == parsed["id"]).first()
            if not existing:
                email_row = Email(
                    gmail_message_id=parsed["id"],
                    thread_id=parsed.get("threadId") or "",
                    account_email=email_address,
                    from_email=parsed.get("from"),
                    subject=parsed.get("subject"),
                    text_body=parsed.get("text_body"),
                    html_body=parsed.get("html_body"),
                    direction=direction_val,
                )
                db.add(email_row)
                saved = db.query(Email).filter(Email.gmail_message_id == parsed["id"]).first()
            else:
                saved = existing

            if background_tasks is not None and saved and saved.direction == EmailDirection.inbound:
                background_tasks.add_task(classify_and_update, saved.id)

        acct.last_history_id = str(history_res.get("historyId", history_id))
        db.update(acct)
    except Exception as e:
        logger.error(f"History fetch error: {e}")
        acct.last_history_id = str(history_id)
        db.update(acct)

    return JSONResponse({"ok": True})

