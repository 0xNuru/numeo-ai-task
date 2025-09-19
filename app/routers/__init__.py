from fastapi import APIRouter
from app.routers.auth import auth as auth_router
from app.routers.web import web as web_router
from app.routers.gmail_webhook import webhook as gmail_webhook_router


router = APIRouter()

router.include_router(web_router)
router.include_router(auth_router)
router.include_router(gmail_webhook_router)