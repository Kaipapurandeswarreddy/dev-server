from fastapi import APIRouter, Depends
from typing import List

import repos.ride.model as repo
import repos.user_types.user as user
import repos.user_types.driver as driver
from config.auth import verify_jwt_admin
from utils.requests import IDRequest

router = APIRouter()


@router.post("/completed/list")
async def list_completed_rides_route(uid: str = Depends(verify_jwt_admin)) -> List[repo.Ride]:
    list = await repo.list_rides(repo.COMPLETED)
    for l in list:
        l.user_id = await user.get_field_value(user.DB[user.COLLECTION_NAME], l.user_id, "name")
        l.driver_id = await driver.get_field_value(driver.DB[driver.COLLECTION_NAME], l.driver_id, "name")
    return list


@router.post("/ongoing/list")
async def list_ongoing_rides_route(uid: str = Depends(verify_jwt_admin)) -> List[repo.Ride]:
    list = await repo.list_rides(repo.ONGOING)
    for l in list:
        l.user_id = await user.get_field_value(user.DB[user.COLLECTION_NAME], l.user_id, "name")
        l.driver_id = await driver.get_field_value(driver.DB[driver.COLLECTION_NAME], l.driver_id, "name")
    return list


@router.post("/user/list")
async def list_ongoing_rides_route(request: IDRequest, uid: str = Depends(verify_jwt_admin)) -> List[repo.Ride]:
    query = {"user_id": request.id}
    list = await repo.list_rides(repo.COMPLETED, query)
    name = await user.get_field_value(user.DB[user.COLLECTION_NAME], request.id, "name")
    for l in list:
        l.user_id = name
        l.driver_id = await driver.get_field_value(driver.DB[driver.COLLECTION_NAME], l.driver_id, "name")
    return list


@router.post("/driver/list")
async def list_ongoing_rides_route(request: IDRequest, uid: str = Depends(verify_jwt_admin)) -> List[repo.Ride]:
    query = {"driver_id": request.id}
    list = await repo.list_rides(repo.COMPLETED, query)
    name = await driver.get_field_value(driver.DB[driver.COLLECTION_NAME], request.id, "name")
    for l in list:
        l.user_id = await user.get_field_value(user.DB[user.COLLECTION_NAME], l.user_id, "name")
        l.driver_id = name
    return list