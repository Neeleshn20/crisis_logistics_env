#grader.py
def grade(metrics):
    inventory = metrics["inventory"]  # {"A": x, "B": y, "C": z}
    values = list(inventory.values())

    # balance score
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    balance = 1 - (variance ** 0.5 / (mean + 1e-6))

    # survival score
    survival = 1.0 if min(values) > 20 else 0.0

    score = 0.6 * balance + 0.4 * survival

    return max(0.0, min(1.0, score))