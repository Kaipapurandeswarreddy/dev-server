import random
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from repos.user_types.auth import send_otp, verify_otp
from config.fcm import send_fcm_notification
from utils.response import LoginResponse, UserFoundResponse
from config.auth import sign_jwt
import repos.user_types.user as user
import repos.records.offer as offer
import repos.records.referrals as referrals

router = APIRouter()


class LoginMobileRequest(BaseModel):
    mobile: str
    app_signature: Optional[str] = None

@router.post("/request/otp", description="Mobile number should be 10 digits only, exclude the country code.")
async def mobile_login_route(request: LoginMobileRequest) -> UserFoundResponse:
    if not await send_otp(request.mobile, request.app_signature):
        raise HTTPException(400, "Error sending OTP!!")

    user_data = await user.find_user_by_mobile(request.mobile)
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
    referral_user = None
    if request.referral_code:
        referral_user = await user.find_user_by_referral_code(request.referral_code)
        if not referral_user:
            raise HTTPException(400, "Invalid referral code")

    if not await verify_otp(request.mobile, request.otp):
        raise HTTPException(400, "Invalid OTP, please try again!")

    user_check = await user.find_user_by_mobile(request.mobile)
    if user_check:
        raise HTTPException(400, "Mobile number already exists")
    
    user_id = await user.insert_user(user.User(name=request.name, mobile=request.mobile))
    token = await sign_jwt(user_id)
    await user.update_jwt(user_id, token)

    if referral_user:
        offer_percentage = random.randint(5, 15)
        await offer.insert_offer(offer.Offer(user_id=referral_user.id, description="Referral reward", offer_percentage=offer_percentage, offer_amount=None))
        await referrals.insert_referral(referrals.Referral(user_type="user", ref_from=referral_user.id, ref_to=user_id, value=f"{offer_percentage} %"))
        if referral_user.fcm_token:
            await send_fcm_notification(referral_user.fcm_token, f"Flat {offer_percentage}% off will be auto applied on your next ride", "Congrats!! Referral reward earned")

    return LoginResponse(token=token)


class LoginVerifyRequest(BaseModel):
    mobile: str
    otp: str

@router.post("/login/verify/otp", description="Mobile number should be 10 digits only, exclude the country code. The response token is the JWT Bearer")
async def mobile_login_verify_route(request: LoginVerifyRequest) -> LoginResponse:
    if not await verify_otp(request.mobile, request.otp):
        raise HTTPException(400, "Invalid OTP, please try again!")

    user_data = await user.find_user_by_mobile(request.mobile)
    if not user_data:
        raise HTTPException(400, "User not found")

    token = await sign_jwt(user_data.id)
    await user.update_jwt(user_data.id, token)
    return LoginResponse(token=token)
