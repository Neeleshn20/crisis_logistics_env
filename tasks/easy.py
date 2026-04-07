#easy.py
from core.models import Supplier

def easy_config():
    return {
        "budget": 10000,
        "max_days": 20,
        "base_demand": 40,
        "demand_std": 5,

        "suppliers": [
            Supplier(id=0, cost=5, reliability=0.9),
            Supplier(id=1, cost=3, reliability=0.7),
        ],

    }