from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import re

from repos.user_types.auth import send_otp, verify_otp
from utils.response import CustomResponse, LoginResponse
from config.auth import sign_jwt
import repos.user_types.admin as admin

router = APIRouter()


class LoginMobileRequest(BaseModel):
    mobile: str

@router.post("/login/mobile", description="Mobile number should be 10 digits only, exclude the country code.")
async def mobile_login_route(request: LoginMobileRequest) -> CustomResponse:
    admin_data = await admin.find_admin_by_mobile(request.mobile)
    if admin_data is None:
        raise HTTPException(400, "Mobile number is not registered as admin. Contact for further information.")

    if await send_otp(request.mobile):
        return CustomResponse(detail=admin_data.name)
    raise HTTPException(400, "Unexpected error occurred, please try again!!")



class LoginMobileVerifyRequest(BaseModel):
    mobile: str
    otp: str

@router.post("/login/mobile/verify", description="Mobile number should be 10 digits only, exclude the country code. The response token is the JWT Bearer")
async def mobile_login_verify_route(request: LoginMobileVerifyRequest) -> LoginResponse:
    if not await verify_otp(request.mobile, request.otp):
        raise HTTPException(400, "Invalid OTP, please verify!!")
    else:
        admin_data = await admin.find_admin_by_mobile(request.mobile)
        if admin_data is None:
            raise HTTPException(400, "Mobile number is not registered as admin. Contact for further information.")

        token = await sign_jwt(admin_data.id)
        await admin.update_jwt(admin_data.id, token)
        return LoginResponse(token= token)
