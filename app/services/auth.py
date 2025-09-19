from typing import Dict, Any
from datetime import datetime
import requests
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from app.models.gmail_account import GmailAccount
from app.core.config import settings


class AuthService:
    def __init__(self):
        pass

    def build_flow(self) -> Flow:
        client_config = {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "project_id": settings.PROJECT_NAME,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOaOGLE_REDIRECT_URI],
                "javascript_origins": ["http://localhost:3000"],
            }
        }
        return Flow.from_client_config(
            client_config,
            scopes=settings.GOOGLE_OAUTH_SCOPES,
            redirect_uri=settings.GOOGLE_REDIRECT_URI,
        )

    def start_google_oauth(self) -> str:
        flow = self.build_flow()
        authorization_url, _state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        return authorization_url

    def handle_google_callback(self, authorization_response_url: str, db) -> Dict[str, Any]:
        flow = self.build_flow()
        flow.fetch_token(authorization_response=authorization_response_url)
        creds = flow.credentials

        gmail = build("gmail", "v1", credentials=creds)
        profile = gmail.users().getProfile(userId="me").execute()
        user_email = profile.get("emailAddress")
        if not user_email:
            raise ValueError("Unable to get user email from Gmail")

        existing = db.query(GmailAccount).filter(GmailAccount.user_email == user_email).first()
        expiry_dt = getattr(creds, "expiry", None)
        scopes_str = " ".join(creds.scopes) if creds.scopes else None
        if existing:
            existing.access_token = creds.token
            existing.refresh_token = creds.refresh_token or existing.refresh_token
            existing.token_expiry = expiry_dt
            existing.scopes = scopes_str
            db.update(existing)
        else:
            acct = GmailAccount(
                user_email=user_email,
                access_token=creds.token,
                refresh_token=creds.refresh_token,
                token_expiry=expiry_dt,
                scopes=scopes_str,
            )
            db.add(acct)

        if settings.GMAIL_PUBSUB_TOPIC:
            try:
                watch_res = gmail.users().watch(
                    userId="me",
                    body={
                        "labelIds": settings.GMAIL_WATCH_LABEL_IDS,
                        "topicName": settings.GMAIL_PUBSUB_TOPIC,
                    },
                ).execute()
                history_id = watch_res.get("historyId")
                expire_ms = watch_res.get("expiration") 
                acct_or_existing = db.query(GmailAccount).filter(GmailAccount.user_email == user_email).first()
                if acct_or_existing:
                    acct_or_existing.last_history_id = str(history_id) if history_id else acct_or_existing.last_history_id
                    if expire_ms:
                        from datetime import datetime, timezone
                        acct_or_existing.watch_expires_at = datetime.fromtimestamp(int(expire_ms)/1000.0, tz=timezone.utc)
                    db.update(acct_or_existing)
            except Exception:
                pass

        return {
            "connected": True,
            "email": user_email,
            "scopes": creds.scopes,
        }

    def list_connected_accounts(self, db) -> Dict[str, Any]:
        rows = db.query(GmailAccount).all()
        return {"accounts": [r.user_email for r in rows]}

    def disconnect_account(self, email: str, db) -> Dict[str, Any]:
        row = db.query(GmailAccount).filter(GmailAccount.user_email == email).first()
        if not row:
            raise KeyError("Account not found")
        token_to_revoke = row.refresh_token or row.access_token
        if token_to_revoke:
            try:
                requests.post(
                    "https://oauth2.googleapis.com/revoke",
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data={"token": token_to_revoke},
                    timeout=5,
                )
            except Exception:
                pass
        row.access_token = None
        row.refresh_token = None
        row.token_expiry = None
        row.disconnected_at = datetime.utcnow()
        db.update(row)
        return {"disconnected": True, "email": email}

auth_service = AuthService()