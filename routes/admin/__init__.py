from fastapi import APIRouter

from .auth import router as auth_router
from .details import router as details_router
from .hospital import router as hospital_router
from .vrf_driver import router as driver_router
from .unvrf_driver import router as unvrf_driver_router
from .user import router as user_router
from .ambulance_types import router as at_router
from .payments import router as payments_router
from .rides import router as rides_router

router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["admin: auth"])
router.include_router(details_router, prefix="/details", tags=["admin: details"])
router.include_router(hospital_router, prefix="/hospital", tags=["admin: hospitals"])
router.include_router(at_router, prefix="/ambulance/types", tags=["admin: ambulance types"])
router.include_router(driver_router, prefix="/driver", tags=["admin: driver"])
router.include_router(unvrf_driver_router, prefix="/driver/unverified", tags=["admin: unverified driver"])
router.include_router(user_router, prefix="/user", tags=["admin: user"])
router.include_router(payments_router, prefix="/payments", tags=["admin: payments"])
router.include_router(rides_router, prefix="/rides", tags=["admin: rides"])
