from pydantic import BaseModel, conlist
from typing import Literal
import string, random


class GeoJSONPoint(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: conlist(float, min_length=2, max_length=2)


class Timing(BaseModel):
    start: str
    end: str

def generate_referral_code(length: int = 6) -> str:
    characters = string.ascii_uppercase + string.digits  # A-Z and 0-9
    return ''.join(random.choices(characters, k=length))