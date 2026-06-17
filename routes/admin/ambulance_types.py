from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List

from repos.user_types.admin import Admin
import repos.data.ambulance_types as at
from config.auth import verify_jwt_admin
from utils.response import CustomResponse

router = APIRouter()
# For ambulance type list router check shared router

@router.post("/add")
async def add_ambulance_type_route(request: at.AmbulanceType, uid: str = Depends(verify_jwt_admin)) -> CustomResponse:
    try:
        request.pricing_tier = at.sort_pricing_tier(request.pricing_tier)
    except ValueError as e:
        raise HTTPException(400, detail=e)
    res = await at.insert_ambulance_type(request)
    if res:
        return CustomResponse(detail="Ambulance Type added successfully")
    else:
        raise HTTPException(400, "Ambulance Type was not added")

@router.post("/update", description="Pass the _id parameter")
async def update_ambulance_type_route(request: at.AmbulanceType, uid: str = Depends(verify_jwt_admin)) -> CustomResponse:
    if not request.id:
        raise HTTPException(400, detail="Parameter _id is missing")
    try:
        request.pricing_tier = at.sort_pricing_tier(request.pricing_tier)
    except ValueError as e:
        raise HTTPException(400, detail=e)
    res = await at.update_ambulance_type_byid(request.id, request)
    if res:
        return CustomResponse(detail="Ambulance Type updated successfully")
    else:
        raise HTTPException(400, "Ambulance Type updated failed")

# class DeleteAmbulanceTypeRequest(BaseModel):
#     type_id: str
#
# @router.post("/delete")
# async def delete_ambulance_type_route(request: DeleteAmbulanceTypeRequest, uid: str = Depends(verify_jwt_admin)) -> CustomResponse:
#     res = await at.delete_ambulance_type_byid(request.type_id)
#     if res:
#         return CustomResponse(detail="Ambulance Type deleted successfully")
#     else:
#         raise HTTPException(400, "Ambulance Type delete failed")