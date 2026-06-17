from fastapi import APIRouter

from .location import router as location_router
from .payment import router as payment_router
from .accepted_rides import router as accepted_router
from .available_rides import router as available_router

router = APIRouter()
router.include_router(location_router, prefix="/location")
router.include_router(payment_router, prefix="/payment")
router.include_router(accepted_router, prefix="/rides/accepted")
router.include_router(available_router, prefix="/rides/available")