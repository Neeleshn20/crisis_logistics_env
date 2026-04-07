from fastapi import FastAPI
from core.env import CrisisLogisticsEnv
from tasks.easy import easy_config

app = FastAPI()
env = CrisisLogisticsEnv(easy_config())

@app.post("/reset")
def reset():
    return env.reset()

@app.post("/step")
def step(action: dict):
    obs, reward, done, info = env.step(action)

    return {
        "state": obs,
        "reward": float(reward),
        "done": bool(done),
        "info": info
    }

@app.get("/state")
def state():
    return env.state()

@app.get("/tasks")
def tasks():
    return ["easy", "medium", "hard"]

@app.get("/grader")
def grader():
    return {"info": "deterministic grader"}

@app.get("/baseline")
def baseline():
    return {"info": "run baseline script"}