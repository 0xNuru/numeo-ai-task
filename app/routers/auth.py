from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from app.services.auth import auth_service
from app.db.load import load



auth = APIRouter(prefix="/auth", tags=["auth"])


@auth.get("/google")
def google_oauth():
    authorization_url = auth_service.start_google_oauth()
    return RedirectResponse(authorization_url)


@auth.get("/google/callback")
def google_oauth_callback(request: Request, db: Session = Depends(load)):
    try:
        result = auth_service.handle_google_callback(str(request.url), db)
        return JSONResponse(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth.get("/google/accounts")
def list_connected_accounts(db: Session = Depends(load)):
    return auth_service.list_connected_accounts(db)


@auth.post("/google/disconnect/{email}")
def disconnect_account(email: str, db: Session = Depends(load)):
    try:
        return auth_service.disconnect_account(email, db)
    except KeyError:
        raise HTTPException(status_code=404, detail="Account not found")