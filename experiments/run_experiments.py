import requests
import csv
import random

BASE_URL = "http://127.0.0.1:8000"


# -------------------------
# API HELPERS
# -------------------------
def reset_env():
    return requests.post(f"{BASE_URL}/reset").json()


def step_env(action):
    res = requests.post(f"{BASE_URL}/step", json=action)

    if res.status_code != 200:
        raise Exception("API ERROR")

    data = res.json()

    return data["state"], data["reward"], data["done"], data.get("info", {})


# -------------------------
# PRODUCT HELPER
# -------------------------
def pick_lowest_inventory_product(obs):
    inv = obs["inventory"]
    return min(inv, key=inv.get)


def pick_highest_inventory_product(obs):
    inv = obs["inventory"]
    return max(inv, key=inv.get)


# -------------------------
# STRATEGIES
# -------------------------
def strategy_balanced(obs):
    return {
        "product": pick_lowest_inventory_product(obs),
        "supplier_id": 0,
        "path_id": 1,
        "quantity": 40,
        "expedite": False
    }


def strategy_risky(obs):
    return {
        "product": pick_lowest_inventory_product(obs),
        "supplier_id": 0,
        "path_id": 0,
        "quantity": 50,
        "expedite": False
    }


def strategy_fast(obs):
    return {
        "product": pick_lowest_inventory_product(obs),
        "supplier_id": 0,
        "path_id": 1,
        "quantity": 60,
        "expedite": True
    }


def strategy_cheap(obs):
    return {
        "product": pick_lowest_inventory_product(obs),
        "supplier_id": 1,
        "path_id": 2,
        "quantity": 40,
        "expedite": False
    }


def strategy_random(obs):
    return {
        "product": random.choice(["A", "B", "C"]),
        "supplier_id": random.choice([0, 1]),
        "path_id": random.choice([0, 1, 2]),
        "quantity": random.choice([20, 40, 60]),
        "expedite": random.choice([True, False])
    }


def strategy_do_nothing(obs):
    return {
        "product": "A",
        "supplier_id": 0,
        "path_id": 1,
        "quantity": 0,
        "expedite": False
    }


# -------------------------
# INTELLIGENT STRATEGY
# -------------------------
def strategy_adaptive(obs):
    inventory = obs["inventory"]
    paths = obs["paths"]
    disruptions = len(obs["disruptions"])

    product = pick_lowest_inventory_product(obs)

    path_items = [(int(k), v) for k, v in paths.items()]

    fastest = min(path_items, key=lambda x: x[1]["time"])[0]
    safest = min(path_items, key=lambda x: x[1]["risk"])[0]
    cheapest = min(path_items, key=lambda x: x[1]["cost"])[0]

    current_inventory = inventory[product]

    if current_inventory < 30:
        return {
            "product": product,
            "supplier_id": 0,
            "path_id": fastest,
            "quantity": 70,
            "expedite": True
        }

    elif current_inventory < 70:
        return {
            "product": product,
            "supplier_id": 0,
            "path_id": safest,
            "quantity": 50,
            "expedite": disruptions > 3
        }

    else:
        return {
            "product": product,
            "supplier_id": 1,
            "path_id": cheapest,
            "quantity": 30,
            "expedite": False
        }


# -------------------------
# RUN ONE STRATEGY
# -------------------------
def run_strategy(name, strategy_fn, steps=20):
    print(f"\n===== Running {name} =====")

    obs = reset_env()

    results = []

    for step in range(steps):
        action = strategy_fn(obs)

        obs, reward, done, _ = step_env(action)

        total_inventory = (
            obs["inventory"]["A"]
            + obs["inventory"]["B"]
            + obs["inventory"]["C"]
        )

        min_inventory = min(
            obs["inventory"]["A"],
            obs["inventory"]["B"],
            obs["inventory"]["C"]
        )

        imbalance = max(
            obs["inventory"]["A"],
            obs["inventory"]["B"],
            obs["inventory"]["C"]
        ) - min_inventory

        row = {
            "strategy": name,
            "step": step,
            "inventory_A": obs["inventory"]["A"],
            "inventory_B": obs["inventory"]["B"],
            "inventory_C": obs["inventory"]["C"],
            "total_inventory": total_inventory,
            "min_inventory": min_inventory,
            "imbalance": imbalance,
            "reward": reward,
            "budget": obs["budget"],
            "num_disruptions": len(obs["disruptions"]),
            "chosen_product": action["product"]
        }

        results.append(row)

        print(
            f"Step {step} → "
            f"A:{row['inventory_A']} B:{row['inventory_B']} C:{row['inventory_C']} "
            f"| Reward: {reward:.3f}"
        )

        if done:
            break
    final_inventory = results[-1]

    print(f"\n📊 Summary for {name}:")
    print(f"Final Reward: {final_inventory['reward']:.3f}")
    print(f"Final Min Inventory: {final_inventory['min_inventory']}")
    print(f"Final Imbalance: {final_inventory['imbalance']}")

    return results


# -------------------------
# SAVE RESULTS
# -------------------------
def save_results(all_results, filename="results.csv"):
    if not all_results:
        return

    keys = all_results[0].keys()
    all_results = sorted(all_results, key=lambda x: (x["strategy"], x["step"]))
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(all_results)

    print(f"\n✅ Results saved to {filename}")


# -------------------------
# RUN ALL STRATEGIES
# -------------------------
def run_all_strategies():
    all_results = []

    strategies = {
        "balanced": strategy_balanced,
        "risky": strategy_risky,
        "fast": strategy_fast,
        "cheap": strategy_cheap,
        "random": strategy_random,
        "adaptive": strategy_adaptive,
        "do_nothing": strategy_do_nothing
    }

    for name, fn in strategies.items():
        results = run_strategy(name, fn)
        all_results.extend(results)

    save_results(all_results)


# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    run_all_strategies()