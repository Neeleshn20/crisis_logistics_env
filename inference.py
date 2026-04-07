import requests
import random

API_URL = "http://localhost:8000"


# -------------------------------
# RESET ENV
# -------------------------------
def reset_env():
    res = requests.post(f"{API_URL}/reset")
    if res.status_code != 200:
        raise Exception("Reset failed")
    return res.json()


# -------------------------------
# STEP ENV
# -------------------------------
def step_env(action):
    res = requests.post(f"{API_URL}/step", json=action)
    if res.status_code != 200:
        raise Exception("Step failed")
    return res.json()


# -------------------------------
# ADAPTIVE STRATEGY (BEST)
# -------------------------------
def adaptive_policy(obs):
    inventory = obs["inventory"]
    paths = obs["paths"]
    suppliers = obs["suppliers"]

    # 🔹 choose product with lowest inventory
    product = min(inventory, key=inventory.get)

    # 🔹 choose safest path (highest reliability)
    best_path = max(paths.items(), key=lambda x: x[1]["reliability"])[0]

    # 🔹 choose best supplier (reliability weighted by cost)
    best_supplier = max(
        suppliers,
        key=lambda s: s["reliability"] / (s["cost"] + 1e-6)
    )["id"]

    # 🔹 dynamic quantity
    base_inventory = inventory[product]

    if base_inventory < 30:
        qty = 50
    elif base_inventory < 60:
        qty = 35
    else:
        qty = 20

    return {
        "product": product,
        "supplier_id": best_supplier,
        "path_id": int(best_path),
        "quantity": int(qty),
        "expedite": False
    }


# -------------------------------
# MAIN LOOP
# -------------------------------
def run():
    print("[START]")

    obs = reset_env()

    total_reward = 0
    step = 0
    done = False

    while not done and step < 50:
        action = adaptive_policy(obs)

        response = step_env(action)

        obs = response["state"]
        reward = response["reward"]
        done = response["done"]

        total_reward += reward

        print(
            f"[STEP] t={step} "
            f"product={action['product']} "
            f"qty={action['quantity']} "
            f"reward={round(reward,3)} "
            f"inv={obs['inventory']}"
        )

        step += 1
        avg_reward = total_reward / step if step > 0 else 0

    print(f"[END] total_reward={round(total_reward,3)} avg_reward={round(avg_reward,3)} steps={step}")
    print(f"[END] total_reward={round(total_reward,3)} steps={step}")

def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step, action, reward, done, error):
    error_val = error if error else "null"
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error_val}", flush=True)

def log_end(success, steps, score, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)
# -------------------------------
# ENTRY
# -------------------------------
if __name__ == "__main__":
    run()