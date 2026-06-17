from fastapi import APIRouter, Depends
from typing import List

from config.auth import verify_jwt
from repos.data.counters import get_counter
import repos.data.ambulance_types as ambulance_types
import repos.data.hospital as hospital

router = APIRouter()

@router.post("/ambulance/types/updates/check")
async def check_ambulance_updates_route(uid: str = Depends(verify_jwt)) -> str:
    counter = await get_counter("ambulance_type")
    return str(counter)

@router.post("/ambulance/types/list")
async def list_ambulance_type_route() -> List[ambulance_types.AmbulanceType]:
    return await ambulance_types.list_ambulance_type()

@router.post("/hospitals/updates/check")
async def check_hospitals_update_route(uid: str = Depends(verify_jwt)) -> str:
    counter = await get_counter("hospitals")
    return str(counter)

@router.post("/hospitals/list")
async def list_hospitals_route() -> List[hospital.Hospital]:
    return await hospital.list_hospital()
