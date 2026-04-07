from pydantic import BaseModel
from typing import List, Literal, Dict, Any


# -------------------------
# TYPES
# -------------------------
RouteStatus = Literal["open", "delayed", "blocked"]


# -------------------------
# SUPPLIER
# -------------------------
class Supplier(BaseModel):
    id: int
    cost: float
    reliability: float


# -------------------------
# SHIPMENT (UPDATED)
# -------------------------
class Shipment(BaseModel):
    supplier_id: int
    path_id: int
    product: str   # 🔥 NEW (A, B, C)
    quantity: int
    eta: int
    delayed: bool = False


# -------------------------
# DISRUPTION
# -------------------------
class Disruption(BaseModel):
    source: str
    target: str
    status: RouteStatus


# -------------------------
# OBSERVATION (UPDATED)
# -------------------------
class Observation(BaseModel):
    day: int
    inventory: Dict[str, int]   # 🔥 CHANGED
    demand_forecast: float
    forecast_uncertainty: float

    incoming_shipments: List[Shipment]
    suppliers: List[Supplier]

    paths: Dict[int, Dict[str, Any]]
    disruptions: List[Disruption]

    budget: float


# -------------------------
# ACTION (UPDATED)
# -------------------------
class Action(BaseModel):
    product: str   # 🔥 NEW
    supplier_id: int
    path_id: int
    quantity: int
    expedite: bool


# -------------------------
# REWARD
# -------------------------
class Reward(BaseModel):
    value: float