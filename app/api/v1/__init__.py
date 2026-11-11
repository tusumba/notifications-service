from fastapi import APIRouter

from app.api.v1 import notifications

router = APIRouter(prefix="/v1")
router.include_router(notifications.router)
