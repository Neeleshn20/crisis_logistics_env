#graph.py
from typing import List, Dict
from pydantic import BaseModel
import random


# -------------------------
# NODE
# -------------------------
class Node(BaseModel):
    id: str
    type: str  # supplier / port / hub / warehouse


# -------------------------
# EDGE
# -------------------------
class Edge(BaseModel):
    source: str
    target: str
    cost: float
    time: int
    reliability: float
    status: str = "open"  # open / delayed / blocked


# -------------------------
# GRAPH
# -------------------------
class Graph:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.adjacency: Dict[str, List[Edge]] = {}

        self._build_nodes()
        self._build_edges()
        self._build_adjacency()
        self.paths = self._define_paths()

    # -------------------------
    # BUILD NODES
    # -------------------------
    def _build_nodes(self):
        nodes = [
            Node(id="S1", type="supplier"),
            Node(id="S2", type="supplier"),
            Node(id="P1", type="port"),
            Node(id="P2", type="port"),
            Node(id="P3", type="port"),
            Node(id="H1", type="hub"),
            Node(id="H2", type="hub"),
            Node(id="W", type="warehouse"),
        ]

        for node in nodes:
            self.nodes[node.id] = node

    # -------------------------
    # BUILD EDGES
    # -------------------------
    def _build_edges(self):
        self.edges = [

            # Supplier → Port
            Edge(source="S1", target="P1", cost=100, time=1, reliability=0.9),
            Edge(source="S2", target="P2", cost=80, time=1, reliability=0.85),
            Edge(source="S2", target="P3", cost=90, time=1, reliability=0.8),

            # Port → Port (sea)
            Edge(source="P1", target="P2", cost=120, time=2, reliability=0.85),
            Edge(source="P2", target="P3", cost=100, time=1, reliability=0.88),
            Edge(source="P1", target="P3", cost=140, time=1, reliability=0.8),

            # Port → Hub
            Edge(source="P3", target="H1", cost=70, time=1, reliability=0.9),
            Edge(source="P2", target="H2", cost=60, time=1, reliability=0.92),

            # Hub → Warehouse
            Edge(source="H1", target="W", cost=50, time=1, reliability=0.95),
            Edge(source="H2", target="W", cost=50, time=1, reliability=0.95),

            Edge(source="S1", target="W", cost=300, time=2, reliability=0.6),  # Direct but risky
        ]

    # -------------------------
    # BUILD ADJACENCY
    # -------------------------
    def _build_adjacency(self):
        self.adjacency = {node_id: [] for node_id in self.nodes}

        for edge in self.edges:
            self.adjacency[edge.source].append(edge)

    # -------------------------
    # DEFINE FIXED PATHS
    # -------------------------
    def _define_paths(self):
        return({
            0: {
                "nodes": ['S1', 'P1', 'P3', 'H1', 'W'],
                "cost": 360,
                "time": 3,
                "risk": 0.7
            },
            1: {
                "nodes": ['S2', 'P2', 'H2', 'W'],
                "cost": 190,
                "time": 2,
                "risk": 0.3
            },
            2: {
                "nodes": ['S2', 'P3', 'H1', 'W'],
                "cost": 210,
                "time": 3,
                "risk": 0.5
            }
        })

    # -------------------------
    # GET EDGES FOR A PATH
    # -------------------------
    def get_path_edges(self, path_id: int) -> List[Edge]:
        path = self.paths[path_id]["nodes"]
        edges = []

        for i in range(len(path) - 1):
            src = path[i]
            dst = path[i + 1]

            for edge in self.adjacency[src]:
                if edge.target == dst:
                    edges.append(edge)
                    break

        return edges

    # -------------------------
    # COMPUTE PATH METRICS
    # -------------------------
    def compute_path_metrics(self, path_id: int):
        edges = self.get_path_edges(path_id)

        total_cost = 0
        total_time = 0
        total_time = max(1, min(total_time, 4))
        reliability = 1.0
        

        for edge in edges:
            total_cost += edge.cost
            total_time += edge.time

            reliability *= edge.reliability
            reliability = max(0.3, reliability)
            # Apply disruptions
            if edge.status == "delayed":
                total_time += random.randint(1, 3)

            if edge.status == "blocked":
                total_time += 3
                reliability *= 0.5
        total_time = max(1, min(total_time, 4))
        if total_time >= 3:
            total_time -= random.choice([0, 1])
        reliability = max(0.3, reliability)
        return total_cost, total_time, reliability

    # -------------------------
    # RESET EDGE STATUS
    # -------------------------
    def reset_edge_status(self):
        for edge in self.edges:
            edge.status = "open"

    # -------------------------
    # APPLY DISRUPTIONS
    # -------------------------
    def apply_disruptions(self, severity=0.2):
        max_disruptions = 3
        count = 0

        for edge in self.edges:
            if count >= max_disruptions:
                break

            rand = random.random()

            if rand < 0.1:
                edge.status = "blocked"
                count += 1

            elif rand < 0.2:
                edge.status = "delayed"
                count += 1
        