from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List

import config.zwitch as zwitch
import repos.records.wallet as wt
import repos.user_types.driver as driver
from config.auth import verify_jwt_driver
from utils.common import generate_reference_no
from utils.response import CustomResponse

router = APIRouter()


@router.post("/get")
async def get_wallet_route(uid: str = Depends(verify_jwt_driver)) -> Optional[driver.WalletDetails]:
    return await driver.get_wallet_details(uid)


@router.post("/update")
async def update_wallet_route(request: driver.WalletDetails, uid: str = Depends(verify_jwt_driver)) -> CustomResponse:
    if not (request.account_no and request.benf_name and request.ifsc_code):
        raise HTTPException(400, "Invalid Account Details")
    
    db_acc_details = await driver.get_wallet_details(uid)
    if not db_acc_details:
        # verification_status = await zwitch.verify_bank_account(request, generate_reference_no())
        # if (verification_status == "failed"):
            # raise HTTPException(400, "Zwitch Beneficiary Account Creation Verification Failed")
        zwitch_beneficiary_id =  await zwitch.create_zwitch_beneficiary(request, uid)

        if not zwitch_beneficiary_id:
            raise HTTPException(400, "Zwitch Beneficiary Account Creation error")
    
        request.benf_id = zwitch_beneficiary_id
    else:
        if db_acc_details.account_no == request.account_no:
            await zwitch.update_zwitch_beneficiary_name(request)
            request.benf_id = db_acc_details.benf_id
        else:
            # verification_status = await zwitch.verify_bank_account(request, generate_reference_no())
            # if (verification_status == "failed"):
                # raise HTTPException(400, "Zwitch Beneficiary Account Creation Verification Failed")
            zwitch_beneficiary_id =  await zwitch.create_zwitch_beneficiary(request, uid)

            if not zwitch_beneficiary_id:
                raise HTTPException(400, "Zwitch Beneficiary Account Creation error")
        
            request.benf_id = zwitch_beneficiary_id
            if not await zwitch.delete_zwitch_beneficiary(db_acc_details.benf_id):
                raise HTTPException(400, "Error Deleting Existing Beneficiary")

    if await driver.update_wallet_details(uid, request):
        return CustomResponse(detail="Wallet details updated successfully")
    raise HTTPException(400, "Error updating wallet details")


class WithdrawlRequest(BaseModel):
    amount: float

@router.post("/withdraw")
async def withdraw_from_wallet_route(request: WithdrawlRequest, uid: str = Depends(verify_jwt_driver)) -> CustomResponse:
    balance = await driver.get_wallet_balance(uid)
    if not balance:
        raise HTTPException(400, "Driver data not found")
    
    if balance < request.amount:
        raise HTTPException(400, "Requested amount is greater than wallet balance!!")
    
    wallet_details: driver.WalletDetails = await driver.get_wallet_details(uid)
    if not wallet_details:
        raise HTTPException(400, "Driver Account Details not found")
    merchant_reference_id: str = generate_reference_no()
    # Rs. 7 for transaction charges
    response = await zwitch.create_transfer(wallet_details, (request.amount-7), merchant_reference_id)
    if not response:
        raise HTTPException(400, "Withdrawl Initiation failed")
    
    if not await driver.update_wallet_balance(uid, -request.amount):
        raise HTTPException(400, "Error withdrawing the amount!!")
    
    data: wt.WalletTransaction = wt.WalletTransaction(
        driver_id=uid, 
        zwitch_beneficiary_id=wallet_details.benf_id, 
        amount=request.amount, 
        account_no=wallet_details.account_no, 
        merchant_reference_id=merchant_reference_id,
        bank_reference_no=response.get("bank_reference_number"),
        zwitch_transfer_id=response.get("id"),
        status=response.get("status"))

    if data.status in ["failed", "pending"]:
        data.error_message = response.get("reason_for_error")

    if not await wt.insert_wallet_transaction(data):
        raise HTTPException(400, "Withdrawl Initiation failed")
    return CustomResponse(detail="Withdrawl initiated, amount will be transferred shortly!!")


@router.post("/transactions/list")    
async def list_transactions_route(uid: str = Depends(verify_jwt_driver)) -> List[wt.WalletTransaction]:
    query = {"driver_id": uid}
    return await wt.list_wallet_transactions(query=query)
