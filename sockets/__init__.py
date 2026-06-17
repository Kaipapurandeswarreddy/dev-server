from fastapi import APIRouter

from .user import router as user_router
from .driver import router as driver_router

router = APIRouter()

router.include_router(user_router, prefix="/user")
router.include_router(driver_router, prefix="/driver")