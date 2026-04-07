from core.models import Supplier

def hard_config():
    return {
        "budget": 6000,
        "max_days": 30,
        "base_demand": 50,
        "demand_std": 12,

        "suppliers": [
            Supplier(id=0, cost=7, reliability=0.88),
            Supplier(id=1, cost=2.5, reliability=0.6),
        ],
    }