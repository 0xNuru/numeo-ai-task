from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from app.db.load import load
from app.models.gmail_account import GmailAccount


web = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="app/templates")


@web.get("/", response_class=HTMLResponse)
def index(request: Request, db=Depends(load)):
    """Minimal server-rendered UI.

    - Lists connected Gmail accounts with their status
    - Provides a "Connect Gmail" button to start OAuth
    - Offers a "Disconnect" action per active account
    """
    accounts = db.query(GmailAccount).all()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "accounts": accounts,
        },
    )

