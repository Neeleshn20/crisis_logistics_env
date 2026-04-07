import requests
import os

# =========================
# CONFIG
# =========================
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

TASKS = ["easy", "medium", "hard"]
MAX_STEPS = 20


# =========================
# LOGGING (STRICT FORMAT)
# =========================
def log_start(task):
    print(f"[START] task={task} env=crisis_logistics model=rule_agent", flush=True)


def log_step(step, action, reward, done, error=None):
    err = error if error else "null"
    done_str = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_str} error={err}",
        flush=True
    )


def log_end(success, steps, score, rewards):
    rewards_str = ",".join([f"{r:.2f}" for r in rewards])
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True
    )


# =========================
# API HELPERS
# =========================
def reset_env(task):
    try:
        res = requests.post(f"{API_BASE_URL}/reset", json={"task": task})
        return res.json()
    except:
        return None


def step_env(action):
    try:
        res = requests.post(f"{API_BASE_URL}/step", json=action)
        return res.json()
    except:
        return None


# =========================
# SIMPLE INTELLIGENT POLICY
# =========================
def choose_action(state):
    inventory = state["inventory"]
    paths = state["paths"]

    # 👉 pick lowest inventory product
    product = min(inventory, key=inventory.get)

    # 👉 choose best path (cost vs reliability tradeoff)
    best_path = None
    best_score = -1

    for pid, p in paths.items():
        score = p["reliability"] / (p["cost"] + 1)
        if score > best_score:
            best_score = score
            best_path = int(pid)

    return {
        "product": product,
        "supplier_id": 0,
        "path_id": best_path,
        "quantity": 40,
        "expedite": False
    }


# =========================
# RUN SINGLE TASK
# =========================
def run_task(task):

    log_start(task)

    rewards = []
    steps_taken = 0
    success = False

    obs = reset_env(task)

    if obs is None:
        log_end(False, 0, 0.0, [])
        return

    state = obs["state"]

    for step in range(1, MAX_STEPS + 1):

        action = choose_action(state)

        result = step_env(action)

        if result is None:
            log_step(step, str(action), 0.0, True, "api_error")
            break

        state = result["state"]
        reward = float(result["reward"])
        done = result["done"]

        rewards.append(reward)
        steps_taken = step

        log_step(step, str(action), reward, done, None)

        if done:
            break

    # =========================
    # SCORE NORMALIZATION
    # =========================
    if len(rewards) > 0:
        avg_reward = sum(rewards) / len(rewards)
    else:
        avg_reward = 0.0

    # clamp score to [0,1]
    score = max(0.0, min(1.0, avg_reward))

    success = score > 0.3  # reasonable threshold

    log_end(success, steps_taken, score, rewards)


# =========================
# MAIN
# =========================
def run():
    for task in TASKS:
        run_task(task)


if __name__ == "__main__":
    run()