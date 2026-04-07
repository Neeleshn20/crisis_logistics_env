import numpy as np
import random

from core.models import *
from core.simulator import simulate_step
from core.graph import Graph


class CrisisLogisticsEnv:

    def __init__(self, config):
        self.config = config
        self.graph = Graph()
        self.paths = self.graph._define_paths()

        # 🔥 MULTI PRODUCT
        self.products = ["A", "B", "C"]

        self.reset()

    def reset(self):
        self.day = 0

        self.inventory = {p: 100 for p in self.products}
        self.budget = self.config["budget"]

        self.shipments = []
        self.disruptions = []

        return self._get_obs()

    def state(self):
        return {
            "day": self.day,
            "inventory": self.inventory,
            "budget": self.budget,
            "shipments": self.shipments,
            "disruptions": self.disruptions
        }

    def step(self, action_dict):
        action = Action(**action_dict)

        product = action.product
        supplier = self.config["suppliers"][action.supplier_id]

        cost_path, time_path, reliability = self.graph.compute_path_metrics(action.path_id)

        total_cost = supplier.cost * action.quantity + cost_path

        if action.expedite:
            total_cost *= 1.5

        if total_cost > self.budget:
            return self._get_obs(), 0.0, False, {"error": "budget_exceeded"}

        path = self.paths[action.path_id]

        eta = max(1, int(path["time"] / 2))
        path_risk = path["risk"]

        # -------------------------
        # DISRUPTIONS
        # -------------------------
        for d in self.disruptions:
            if "nodes" in path:
                if any(node in path["nodes"] for node in [d.get("source"), d.get("target")]):
                    eta += int(2 * d.get("severity", 1))
                    path_risk += 0.2 * d.get("severity", 1)

        eta = max(1, min(eta, 4))
        path_risk = min(1.0, path_risk)

        if action.expedite:
            eta = max(1, eta - 1)

        shipment = Shipment(
            supplier_id=action.supplier_id,
            path_id=action.path_id,
            product=product,
            quantity=action.quantity,
            eta=eta,
            delayed=False
        )

        self.shipments.append(shipment)

        if random.random() < path_risk:
            shipment.quantity = 0
            shipment.delayed = True

        # -------------------------
        # SIMULATION
        # -------------------------
        fulfilled, delay_penalty = simulate_step(self)

        # -------------------------
        # GRAPH UPDATES
        # -------------------------
        self.graph.reset_edge_status()
        self.graph.apply_disruptions(severity=0.3)

        # -------------------------
        # BUDGET
        # -------------------------
        self.budget -= total_cost

        # -------------------------
        # DEMAND (MULTI)
        # -------------------------
        demand = {p: self._sample_demand() for p in self.products}

        total_fulfillment = 0
        total_demand = 0

        for p in self.products:
            demand_noise = random.uniform(0.35, 0.45)
            used = min(self.inventory[p], int(demand_noise * demand[p]))

            self.inventory[p] -= used

            total_fulfillment += used
            total_demand += demand[p]

        fulfillment_ratio = total_fulfillment / (total_demand + 1e-6)

        # -------------------------
        # STOCKOUT
        # -------------------------
        if min(self.inventory.values()) <= 5:
            self.day += 1
            return self._get_obs(), 0.0, True, {"reason": "stockout"}

        # -------------------------
        # PENALTIES
        # -------------------------
        total_inventory = sum(self.inventory.values())
        target_inventory = 80 * len(self.products)  # = 240 dynamic

        inventory_deviation = abs(total_inventory - target_inventory) / target_inventory

        stockout_penalty = max(0, demand[product] - self.inventory[product]) / (demand[product] + 1e-6)
        stockout_penalty *= 0.5
        cost_penalty = total_cost / 300


        # 🔥 BALANCE PENALTY
        inv_values = np.array(list(self.inventory.values()))
        imbalance = np.std(inv_values)
        balance_penalty = imbalance / (np.mean(inv_values) + 1e-6)

        # -------------------------
        # REWARD
        # -------------------------
        reward = (
            2.5 * fulfillment_ratio
            - 0.5 * delay_penalty
            - 0.4 * cost_penalty
            - 1.0 * stockout_penalty
            - 0.4 * inventory_deviation
            - 0.5 * balance_penalty
        )
        if action.quantity < 10:
            reward -= 0.15
        # small baseline (not too high)
        reward += 0.1

        # -------------------------
        # DONE
        # -------------------------
        self.day += 1
        done = self.day >= self.config["max_days"] or self.budget <= 0

        if done:
            reward = 0.0

        # FINAL clamp (ONLY ONCE)
        reward = max(0.0, min(1.0, reward))

        return self._get_obs(), reward, done, {}

    def _sample_demand(self):
        base = self.config["base_demand"]
        noise = np.random.normal(0, self.config["demand_std"])

        demand = base + noise
        demand = max(15, min(demand, 45))

        return int(demand)

    def _get_obs(self):
        paths_info = {}

        for pid, path in self.graph.paths.items():
            cost, time, reliability = self.graph.compute_path_metrics(pid)

            paths_info[pid] = {
                "nodes": path["nodes"],
                "cost": cost,
                "time": time,
                "reliability": reliability,
                "risk": 1 - reliability
            }

        return Observation(
            day=self.day,
            inventory=self.inventory,
            demand_forecast=self.config["base_demand"],
            forecast_uncertainty=self.config["demand_std"],
            incoming_shipments=self.shipments,
            suppliers=self.config["suppliers"],
            paths=paths_info,
            disruptions=[
                {
                    "source": edge.source,
                    "target": edge.target,
                    "status": edge.status
                }
                for edge in self.graph.edges if edge.status != "open"
            ],
            budget=self.budget
        )