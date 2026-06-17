from fastapi import APIRouter

from .user_payment import router as user_router
from .zwitch import router as zwitch_router

router = APIRouter()
router.include_router(user_router, prefix="/user", tags=["user: payment"])
router.include_router(zwitch_router, prefix="/driver", tags=["driver: payout"])