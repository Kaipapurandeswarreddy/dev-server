from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List

import repos.data.hospital as hospital
from config.auth import verify_jwt_admin
from utils.response import CustomResponse
from utils.translation import translate_field

router = APIRouter()
# For hospital list route check shared router

@router.post("/add")
async def add_hospital_route(request: hospital.Hospital, uid: str = Depends(verify_jwt_admin)) -> CustomResponse:
    request.name = await translate_field(request.name) if isinstance(request.name, str) else request.name
    request.address = await translate_field(request.address) if isinstance(request.address, str) else request.address
    request.city = await translate_field(request.city) if isinstance(request.city, str) else request.city
    res = await hospital.insert_hospital(request)
    if res:
        return CustomResponse(detail="Hospital added successfully")
    else:
        raise HTTPException(400, "Hospital add failed")

@router.post("/update", description="Pass the _id parameter")
async def update_hospital_route(request: hospital.Hospital, uid: str = Depends(verify_jwt_admin)) -> CustomResponse:
    if not request.id:
        raise HTTPException(400, detail="Parameter _id is missing")
    request.name = await translate_field(request.name) if isinstance(request.name, str) else request.name
    request.address = await translate_field(request.address) if isinstance(request.address, str) else request.address
    request.city = await translate_field(request.city) if isinstance(request.city, str) else request.city
    res = await hospital.update_hospital_byid(request.id, request)
    if res:
        return CustomResponse(detail="Hospital updated successfully")
    else:
        raise HTTPException(400, "Hospital updated failed")

class DeleteHospitalRequest(BaseModel):
    hospital_id: str

@router.post("/delete")
async def delete_hospital_route(request: DeleteHospitalRequest, uid: str = Depends(verify_jwt_admin)) -> CustomResponse:
    res = await hospital.delete_hospital_byid(request.hospital_id)
    if res:
        return CustomResponse(detail="Hospital deleted successfully")
    else:
        raise HTTPException(400, "Hospital delete failed")