import random

def simulate_step(env):
    fulfilled = 0
    delay_penalty = 0

    for shipment in env.shipments:
        shipment.eta -= 1

        if shipment.eta <= 0:
            if random.random() < env.config["suppliers"][shipment.supplier_id].reliability:
                
                # ✅ ADD TO CORRECT PRODUCT
                env.inventory[shipment.product] += shipment.quantity

                fulfilled += shipment.quantity
            else:
                delay_penalty += 0.2

    # remove delivered shipments
    env.shipments = [s for s in env.shipments if s.eta > 0]

    return fulfilled, delay_penalty