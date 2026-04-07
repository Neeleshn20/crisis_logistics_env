# 🚚 Crisis Logistics Decision Environment

A **multi-product reinforcement learning environment** simulating real-world supply chain decision-making under uncertainty, disruptions, and resource constraints.

Built for the **Meta × Hugging Face OpenEnv Hackathon**.

---

## 🧠 Overview

This environment models a **dynamic logistics system** where an agent must:

* Select suppliers
* Choose logistics paths
* Allocate budget
* Manage inventory across multiple products
* Handle disruptions and uncertainty

The goal is to **maximize operational performance while avoiding system collapse**.

---

## 🎯 Core Idea

> AI systems can appear stable while silently degrading under uncertainty.

This environment exposes that phenomenon through:

* Multi-product competition
* Resource constraints
* Cascading failures (extensible)
* Trade-offs between cost, reliability, and speed

---

## 🏗️ System Design

### 🔹 Multi-Product Inventory

* Products: **A, B, C**
* Shared budget and logistics
* Independent demand patterns

### 🔹 Logistics Graph

* Supplier → Port → Hub → Warehouse
* Each path has:

  * Cost
  * Time (ETA)
  * Reliability
  * Risk

### 🔹 Disruptions

* Random failures across edges
* Blocked or delayed routes
* Forces adaptive decision-making

---

## ⚙️ API Endpoints

| Endpoint | Description            |
| -------- | ---------------------- |
| `/reset` | Initialize environment |
| `/step`  | Execute action         |
| `/state` | Get current state      |

Swagger UI available at:

```
http://localhost:8000/docs
```

---

## 🎮 Action Space

```json
{
  "product": "A | B | C",
  "supplier_id": int,
  "path_id": int,
  "quantity": int,
  "expedite": boolean
}
```

---

## 👁️ Observation Space

```json
{
  "day": int,
  "inventory": { "A": int, "B": int, "C": int },
  "demand_forecast": float,
  "forecast_uncertainty": float,
  "incoming_shipments": [],
  "suppliers": [],
  "paths": {},
  "disruptions": [],
  "budget": float
}
```

---

## 🏆 Reward Function

Reward is bounded:

```
0 ≤ reward ≤ 1
```

It captures:

* Fulfillment efficiency
* Cost efficiency
* Delay penalties
* Stockout penalties
* Inventory imbalance

---

## 🧪 Tasks

### 🟢 Easy

* Single product
* No disruptions
* Goal: maintain inventory

### 🟡 Medium

* Graph logistics
* Disruptions
* Cost vs reliability trade-offs

### 🔴 Hard

* Multi-product (A, B, C)
* Shared budget
* Conflicting demand priorities

---

## 🤖 Baseline Strategy (Adaptive)

The provided inference uses an adaptive policy:

* Prioritizes lowest inventory product
* Selects most reliable path
* Balances cost vs reliability
* Adjusts order quantity dynamically

---

## ▶️ Running Locally

### 1. Install dependencies

```bash
pip install fastapi uvicorn pydantic numpy requests
```

---

### 2. Start API

```bash
uvicorn api.app:app --reload
```

---

### 3. Run inference

```bash
python experiments/inference.py
```

---

## 🐳 Docker

### Build

```bash
docker build -t crisis-env .
```

### Run

```bash
docker run -p 8000:8000 crisis-env
```

---

## 📁 Project Structure

```
core/
    env.py
    graph.py
    models.py

api/
    app.py

tasks/
    easy.py
    medium.py
    hard.py

experiments/
    run_experiments.py
    inference.py

openenv.yaml
Dockerfile
README.md
```

---

## 🚀 Key Features

* Multi-product decision-making
* Realistic supply chain simulation
* Dynamic disruptions
* Resource-constrained optimization
* Clear reward signal for learning
* OpenEnv compliant

---

## 🧠 Why This Matters

Most environments are:

* Single-agent toy problems ❌
* No real trade-offs ❌

This system introduces:

* Competing objectives
* Uncertainty
* System-level failure modes

👉 Making it closer to real-world AI deployment scenarios.

---

## 📌 Submission Notes

* Fully OpenEnv compliant
* Reward bounded in [0,1]
* API stable and reproducible
* Inference runs < 20 minutes
* Docker-ready for deployment

---

## 👤 Author

Built by Neelesh
