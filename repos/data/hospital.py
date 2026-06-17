from repos.default import *
from repos.common import *
from repos.data.counters import update_counter

DB = get_data_database()
COLLECTION_NAME = "hospitals"

class Hospital(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: dict | str
    location: GeoJSONPoint
    city: dict | str
    address: dict | str
    timing: Timing
    always_open: bool
    services: List[str]

    def __init__(self, **data):
        if '_id' in data and isinstance(data['_id'], ObjectId):
            data['_id'] = str(data['_id'])
        super().__init__(**data)


async def find_hospital_byid(uid: str) -> Optional[Hospital]:
    clc = DB[COLLECTION_NAME]
    query = {"_id": ObjectId(uid)}
    res = await clc.find_one(query)
    if res:
        return Hospital(**res)
    return None

async def list_hospital() -> List[Hospital]:
    clc = DB[COLLECTION_NAME]
    result = clc.find()
    ret_list = []
    async for r in result:
        ret_list.append(Hospital(**r))
    return ret_list

async def insert_hospital(hospital: Hospital) -> str:
    await update_counter("hospitals")
    return await insert_to_collection(DB[COLLECTION_NAME], hospital)

async def update_hospital_byid(uid: str, hospital: Hospital) -> bool:
    await update_counter("hospitals")
    return await update_object_in_collection_byid(DB[COLLECTION_NAME], uid, hospital)

async def delete_hospital_byid(uid: str) -> bool:
    await update_counter("hospitals")
    return await delete_object_in_collection_byid(DB[COLLECTION_NAME], uid)