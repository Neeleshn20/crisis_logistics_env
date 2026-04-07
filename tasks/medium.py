from core.models import Supplier

def medium_config():
    return {
        "budget": 8000,
        "max_days": 25,
        "base_demand": 45,
        "demand_std": 8,

        "suppliers": [
            Supplier(id=0, cost=6, reliability=0.9),
            Supplier(id=1, cost=3, reliability=0.65),
        ],
    }