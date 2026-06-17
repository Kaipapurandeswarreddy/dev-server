from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List

import repos.user_types.driver as driver
from config.auth import verify_jwt_admin
from utils.response import CustomResponse, ListResponse
from utils.requests import IDRequest, ListRequest

router = APIRouter()


@router.post("/details")
async def request_driver_details_route(request: IDRequest, uid: str = Depends(verify_jwt_admin)) -> driver.DriverDetails:
    driver_data = await driver.find_driver_details_byid(request.id)
    if not driver_data:
        raise HTTPException(404, "Driver data not found")
    return driver_data

@router.post("/list")
async def list_drivers_route(request: ListRequest, uid:str = Depends(verify_jwt_admin)) -> ListResponse:
    d_list = await driver.list_driver(request.skip)
    d_count = await driver.list_driver_count()
    return ListResponse(total=d_count, data=d_list)


@router.post("/add")
async def add_driver_route(request: driver.Driver, uid: str = Depends(verify_jwt_admin)) -> CustomResponse:
    if await driver.insert_driver(request):
        return CustomResponse(detail="Driver added successfully")
    raise HTTPException(400, "Driver add failed")

@router.post("/update")
async def update_driver_route(request: driver.Driver, uid: str = Depends(verify_jwt_admin)) -> CustomResponse:
    if not request.id:
        raise HTTPException(400, detail="Parameter _id is missing")

    driver_data = await driver.find_driver_by_id(request.id)
    driver_data.name = request.name
    driver_data.mobile = request.mobile
    driver_data.photo = request.photo
    driver_data.vehicle_type = request.vehicle_type
    driver_data.vehicle_registration = request.vehicle_registration
    driver_data.details = request.details

    res = await driver.update_driver(request.id, driver_data)
    if res:
        return CustomResponse(detail="Driver updated successfully")
    raise HTTPException(400, "Driver updated failed")

@router.post("/delete")
async def delete_driver_route(request: IDRequest, uid: str = Depends(verify_jwt_admin)) -> CustomResponse:
    res = await driver.delete_driver_byid(request.id)
    if res:
        return CustomResponse(detail="Driver deleted successfully")
    raise HTTPException(400, "Driver delete failed")