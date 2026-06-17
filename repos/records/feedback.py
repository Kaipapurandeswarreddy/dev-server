from repos.default import *
from datetime import datetime, timezone

DB = get_records_database()
COLLECTION_NAME = "feedback"

class Feedback(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_type: str
    user_id: str
    content: str
    resolved: bool = False

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("id", mode="before")
    def convert_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v
    

async def list_feedbacks(query: dict = None, skip: int = 0, limit: int = 100) -> List[Feedback]:
    if query is None:
        query = {}
    clc = DB[COLLECTION_NAME]
    result = clc.find(query).sort("_id", -1).skip(skip).limit(limit)
    ret_list = []
    async for r in result:
        ret_list.append(Feedback(**r))
    return ret_list

async def insert_feedback(feedback: Feedback) -> str:
    return await insert_to_collection(DB[COLLECTION_NAME], feedback)

async def delete_feedback_byid(uid: str) -> bool:
    return await delete_object_in_collection_byid(DB[COLLECTION_NAME], uid)