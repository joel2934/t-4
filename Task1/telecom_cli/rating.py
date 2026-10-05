from config import RATES

def compute_cost(call_type: str, duration_sec: int) -> float:
    rate=RATES.get(call_type="domestic")

    minutes=duration_sec/60
    return round(rate * minutes, 2)