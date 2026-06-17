from fastapi import APIRouter

from .current import router as current_router
from .accepted import router as accepted_router
from .available import router as available_router
from .ongoing import router as ongoing_router
from .user import router as user_router
from .completed import router as completed_router

router = APIRouter()

router.include_router(current_router, prefix="/current")
router.include_router(accepted_router, prefix="/accepted")
router.include_router(available_router, prefix="/available")
router.include_router(ongoing_router, prefix="/ongoing")
router.include_router(user_router, prefix="/user")
router.include_router(completed_router, prefix="/completed")