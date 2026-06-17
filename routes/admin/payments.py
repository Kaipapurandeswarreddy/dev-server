from fastapi import APIRouter, Depends
from typing import List

import repos.records.payment as repo
from config.auth import verify_jwt_admin

router = APIRouter()


@router.post("/list")
async def list_drivers_route(uid: str = Depends(verify_jwt_admin)) -> List[repo.Payment]:
    return await repo.list_payments()