from fastapi import APIRouter, Depends
from typing import List

import repos.user_types.user as repo
from config.auth import verify_jwt_admin

router = APIRouter()


@router.post("/list")
async def list_drivers_route(uid: str = Depends(verify_jwt_admin)) -> List[repo.User]:
    return await repo.list_user()

# @router.post("/add")
# async def add_driver_route(request: user.Driver, uid:str=Depends(verify_jwt_admin)) -> CustomResponse:
#     if request.referral_code:
#         raise HTTPException(400, detail="Referral code should not be mentioned")
#     await user.insert_driver(request)
#     return CustomResponse(detail="Driver added successfully")
#
# @router.post("/update")
# async def update_driver_route(request: user.Driver, uid:str=Depends(verify_jwt_admin)) -> CustomResponse:
#     await user.update_driver(request.id, request)
#     return CustomResponse(detail="Driver updated successfully")
#
# class DriverDeleteRequest(BaseModel):
#     driver_id: str
#
# @router.post("/delete")
# async def delete_driver_route(request: DriverDeleteRequest, uid:str=Depends(verify_jwt_admin)) -> CustomResponse:
#     await user.delete_driver_byid(request.driver_id)
#     return CustomResponse(detail="Driver deleted successfully")