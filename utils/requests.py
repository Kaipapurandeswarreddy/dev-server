from pydantic import BaseModel

class FcmRequest(BaseModel):
    fcm_token: str

class IDRequest(BaseModel):
    id: str

class RideIDRequest(BaseModel):
    ride_id: str

class ListRequest(BaseModel):
    skip: int
    search: str | None = None
