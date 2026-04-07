import random
from core.models import Disruption

def update_disruptions(env):

    env.disruptions = []

    for edge in env.graph.edges:
        rand = random.random()

        if rand < 0.2:
            edge.status = "blocked"

            env.disruptions.append(
                Disruption(
                    source=edge.source,
                    target=edge.target,
                    status="blocked"
                )
            )

        elif rand < 0.35:
            edge.status = "delayed"

            env.disruptions.append(
                Disruption(
                    source=edge.source,
                    target=edge.target,
                    status="delayed"
                )
            )