from fastapi import APIRouter

from .data import router as data_router
from .call_mask import router as call_router
from .feedback import router as feedback_router

router = APIRouter()
router.include_router(data_router, prefix="/data")
router.include_router(feedback_router, prefix="/feedback")
router.include_router(call_router)