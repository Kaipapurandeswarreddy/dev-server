from repos.default import *
from repos.data.counters import update_counter

DB = get_data_database()
COLLECTION_NAME = "ambulance_type"

class AmbulancePricingTier(BaseModel):
    threshold_distance: float
    cost_per_km: float


class AmbulanceType(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    photo: str
    helper_included: bool
    otp_required: bool
    listing_threshold: float
    base_fare: float
    driver_share: float # in percentage
    pricing_tier: List[AmbulancePricingTier]

    def __init__(self, **data):
        if '_id' in data and isinstance(data['_id'], ObjectId):
            data['_id'] = str(data['_id'])
        super().__init__(**data)


async def find_ambulance_type_byid(uid: str) -> Optional[AmbulanceType]:
    clc = DB[COLLECTION_NAME]
    query = {"_id": ObjectId(uid)}
    res = await clc.find_one(query)
    if res:
        return AmbulanceType(**res)
    return None

async def list_ambulance_type() -> List[AmbulanceType]:
    clc = DB[COLLECTION_NAME]
    result = clc.find()
    ret_list = []
    async for r in result:
        ret_list.append(AmbulanceType(**r))
    return ret_list

async def get_driver_share(uid: str) -> Optional[float]:
    return await get_field_value(DB[COLLECTION_NAME], uid, "driver_share")

async def get_listing_threshold(uid: str) -> Optional[float]:
    return await get_field_value(DB[COLLECTION_NAME], uid, "listing_threshold")

async def insert_ambulance_type(ambulance_type: AmbulanceType) -> str:
    await update_counter("ambulance_type")
    return await insert_to_collection(DB[COLLECTION_NAME], ambulance_type)


async def update_ambulance_type_byid(uid: str, ambulance_type: AmbulanceType) -> bool:
    await update_counter("ambulance_type")
    return await update_object_in_collection_byid(DB[COLLECTION_NAME], uid, ambulance_type)


async def delete_ambulance_type_byid(uid: str) -> bool:
    await update_counter("ambulance_type")
    return await delete_object_in_collection_byid(DB[COLLECTION_NAME], uid)


def sort_pricing_tier(pricing: List[AmbulancePricingTier]) -> List[AmbulancePricingTier]:
    # Check for duplicate threshold distances
    seen_thresholds = set()
    for tier in pricing:
        if tier.threshold_distance in seen_thresholds:
            raise ValueError(f"Duplicate thresholdDistance found: {tier.threshold_distance}")
        seen_thresholds.add(tier.threshold_distance)

    # Sorts pricing tiers by threshold distance in ascending order.
    return sorted(pricing, key=lambda p: p.threshold_distance)


def calculate_fare(distance: float, base_fare: float, pricing: List[AmbulancePricingTier]) -> float:
    """
    Calculates the fare based on distance traveled and sorted pricing tiers.

    :param base_fare: Base Fare included above per km costs
    :param distance: Total distance traveled
    :param pricing: List of sorted AmbulancePricingTier objects
    :return: Total cost for the trip
    """
    pricing = sort_pricing_tier(pricing)  # Ensure tiers are sorted
    total_cost = 0.0
    previous_threshold = 0.0  # To track the last tier limit

    for tier in pricing:
        if distance <= previous_threshold:
            break  # No more distance to charge

        applicable_distance = min(distance, tier.threshold_distance) - previous_threshold
        total_cost += applicable_distance * tier.cost_per_km
        previous_threshold = tier.threshold_distance

    return total_cost + base_fare
