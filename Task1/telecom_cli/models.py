from rating import compute_cost
from config import DEFAULT_FRAUD_THRESHOLD_SEC

class Subscriber:
    def __init__(self , msisdn , plan_type):
        self.msisdn=msisdn
        self.plan_type=plan_type
        self.calls=[]

    def total_cost(self) -> float:
        total=0

        for call in self.calls:
            total+=compute_cost(call["call_type"],call["duration_sec"])

        return total


class CDR:
    def __init__(self, msisdn, call_type, duration_sec):
        self.msisdn = msisdn
        self.call_type = call_type
        self.duration_sec = duration_sec

    def is_suspicious(self, threshold=DEFAULT_FRAUD_THRESHOLD_SEC):
        """
        Example fraud rules (FR5):
        1. Call duration exceeds threshold.
        2. International call lasting over 30 minutes.
        """
        if self.duration_sec > threshold:
            return True

        if self.call_type == "international" and self.duration_sec > 1800:
            return True

        return False
