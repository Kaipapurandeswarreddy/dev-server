from fastapi import APIRouter

from .auth import router as auth_router
from .details import router as details_router
from .rides import router as rides_router
from .payment import router as payment_router

router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["user: auth"])
router.include_router(details_router, prefix="/details", tags=["user: details"])
router.include_router(rides_router, prefix="/rides", tags=["user: rides"])
router.include_router(payment_router, prefix="/payment", tags=["user: payment"])
