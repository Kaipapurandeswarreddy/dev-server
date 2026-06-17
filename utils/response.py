from pydantic import BaseModel
from typing import Optional, List


class CustomResponse(BaseModel):
    detail: str

class UserFoundResponse(BaseModel):
    found: bool
    name: Optional[str]

class LoginResponse(BaseModel):
    token: str

class ListResponse(BaseModel):
    total: int
    data: List