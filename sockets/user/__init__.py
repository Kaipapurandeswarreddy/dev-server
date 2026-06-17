from fastapi import APIRouter

from .ongoing_rides import router as ongoing_rides_router
from .accepted_rides import router as accepted_rides_router

router = APIRouter()

router.include_router(ongoing_rides_router, prefix="/rides/ongoing")
router.include_router(accepted_rides_router, prefix="/rides/accepted")