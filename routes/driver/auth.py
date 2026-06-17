from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from config.fcm import send_fcm_notification
from repos.user_types.auth import send_otp, verify_otp
from utils.response import CustomResponse, LoginResponse, UserFoundResponse
from config.auth import sign_jwt
import repos.records.referrals as referrals
import repos.user_types.driver as driver
import repos.user_types.unverified_driver as unverified_driver

router = APIRouter()


class LoginMobileRequest(BaseModel):
    mobile: str

@router.post("/request/otp", description="Mobile number should be 10 digits only, exclude the country code.")
async def mobile_login_route(request: LoginMobileRequest) -> UserFoundResponse:
    if not await send_otp(request.mobile):
        raise HTTPException(400, "Error sending OTP!!")

    user_data = await driver.find_driver_by_mobile(request.mobile)
    if not user_data:
        user_data = await unverified_driver.find_driver_by_mobile(request.mobile)
    if user_data:
        return UserFoundResponse(found=True, name=user_data.name)
    else:
        return UserFoundResponse(found=False, name=None)


class SignupVerifyRequest(BaseModel):
    name: str
    mobile: str
    otp: str
    referral_code: Optional[str] = None

@router.post("/signup/verify/otp", description="Mobile number should be 10 digits only, exclude the country code. The response token is the JWT Bearer")
async def mobile_signup_verify_route(request: SignupVerifyRequest) -> LoginResponse:
    referral_driver = None
    if request.referral_code:
        referral_driver = await driver.find_driver_by_referral_code(request.referral_code)
        if not referral_driver:
            raise HTTPException(400, "Invalid referral code")

    if not await verify_otp(request.mobile, request.otp):
        raise HTTPException(400, "Invalid OTP, please try again!")

    user_check = await driver.find_driver_by_mobile(request.mobile)
    if user_check:
        raise HTTPException(400, "Mobile number already exists")

    user_check = await unverified_driver.find_driver_by_mobile(request.mobile)
    if user_check:
        raise HTTPException(400, "Mobile number already exists")

    user_id = await unverified_driver.insert_driver(unverified_driver.UnverifiedDriver(name=request.name, mobile=request.mobile, under_progress=False))
    if not user_id:
        raise HTTPException(400, "Unexpected error occurred, please login again")
    token = await sign_jwt(user_id)
    await unverified_driver.update_jwt(user_id, token)

    if referral_driver:
        await referrals.insert_referral(referrals.Referral(user_type="driver", ref_from=referral_driver.id, ref_to=user_id, value=f"₹500"))
        if referral_driver.fcm_token:
            await send_fcm_notification(referral_driver.fcm_token, "₹500 will be debited to your wallet once your friend finishes his first 5 rides", "Congrats!! Referral reward earned")

    return LoginResponse(token=token)


class LoginVerifyRequest(BaseModel):
    mobile: str
    otp: str

@router.post("/login/verify/otp", description="Mobile number should be 10 digits only, exclude the country code. The response token is the JWT Bearer")
async def mobile_login_verify_route(request: LoginVerifyRequest) -> LoginResponse:
    if not await verify_otp(request.mobile, request.otp):
        raise HTTPException(400, "Invalid OTP, please try again!")

    user_data = await driver.find_driver_by_mobile(request.mobile)
    if user_data:
        token = await sign_jwt(user_data.id)
        await driver.update_jwt(user_data.id, token)
        return LoginResponse(token=token)

    user_data = await unverified_driver.find_driver_by_mobile(request.mobile)
    if user_data:
        token = await sign_jwt(user_data.id)
        await unverified_driver.update_jwt(user_data.id, token)
        return LoginResponse(token=token)

    raise HTTPException(400, "User not found")

