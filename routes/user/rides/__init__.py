from fastapi import APIRouter

from .completed import router as completed_router
from .driver import router as driver_router
from .search import router as search_router
from .current import router as current_router
from .accepted import router as accepted_router

router = APIRouter()
router.include_router(completed_router, prefix="/completed")
router.include_router(driver_router, prefix="/driver")
router.include_router(search_router, prefix="/search")
router.include_router(current_router, prefix="/current")
router.include_router(accepted_router, prefix="/accepted")