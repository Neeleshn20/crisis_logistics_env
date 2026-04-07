import random
import requests

URL = "http://localhost:8000"

def run():
    obs = requests.post(f"{URL}/reset").json()

    total_reward = 0

    for _ in range(50):
        action = {
            "product": random.choice(["A", "B", "C"]),  # 🔥 REQUIRED
            "supplier_id": random.randint(0, 1),
            "path_id": random.randint(0, 2),           # 🔥 FIXED
            "quantity": random.randint(10, 50),
            "expedite": random.choice([True, False])
        }

        response = requests.post(f"{URL}/step", json=action)

        if response.status_code != 200:
            print("API ERROR")
            break

        data = response.json()

        reward = data.get("reward", 0)
        done = data.get("done", False)

        total_reward += reward

        if done:
            break

    print("Total reward:", total_reward)


if __name__ == "__main__":
    run()