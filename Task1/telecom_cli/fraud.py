from models import CDR


def detect_fraud(cdrs, threshold):

    suspicious = []

    for record in cdrs:

        cdr = CDR(
            record["msisdn"],
            record["call_type"],
            record["duration_sec"]
        )

        if cdr.is_suspicious(threshold):
            suspicious.append(record)

    return suspicious