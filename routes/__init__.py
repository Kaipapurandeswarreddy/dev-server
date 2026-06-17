from fastapi import APIRouter
import os

from .shared import router as shared_router
from .admin import router as admin_router
from .driver import router as driver_router
from .user import router as user_router

router = APIRouter()
router.include_router(user_router, prefix="/user")
router.include_router(driver_router, prefix="/driver")
router.include_router(admin_router, prefix="/admin")
router.include_router(shared_router, tags=["routes accessible to all user types"])
