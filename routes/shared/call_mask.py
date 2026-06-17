from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from config.auth import verify_jwt
from config.cloudshope import initiate_call_masking
from utils.response import CustomResponse

router = APIRouter()

class CallMaskingRequest(BaseModel):
    from_number: str
    to_number: str

@router.post("/call/mask")
async def call_masking_router(data: CallMaskingRequest, uid: str = Depends(verify_jwt)) -> CustomResponse:
    try:
        number = await initiate_call_masking(data.from_number, data.to_number)
        return CustomResponse(detail=number)
    except Exception as e:
        print(f"Cloudshope error: {e}")
        raise HTTPException(400, "Error placing the call, please try again!")