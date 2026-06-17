from fastapi import APIRouter

from .auth import router as auth_router
from .verification import router as verification_router
from .vrf_details import router as vrf_details_router
from .unvrf_details import router as unvrf_details_router
from .rides import router as rides_router
from .wallet import router as wallet_router
from .payment import router as payment_router

router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["driver: auth"])
router.include_router(verification_router, prefix="/verification", tags=["driver: verification"])
router.include_router(vrf_details_router, prefix="/verified/details", tags=["driver: verified details"])
router.include_router(unvrf_details_router, prefix="/unverified/details", tags=["driver: unverified details"])
router.include_router(rides_router, prefix="/rides", tags=["driver: rides"])
router.include_router(wallet_router, prefix="/wallet", tags=["driver: wallet"])
router.include_router(payment_router, prefix="/payment", tags=["driver: payments"])