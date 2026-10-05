import argparse
import datetime
import logging
import sys

from io_utils import (
    load_subscribers,
    load_cdrs
)

from reporting import write_report
from fraud import detect_fraud


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--subscribers", required=True)
    parser.add_argument("--cdrs", required=True)
    parser.add_argument("--output", required=True)

    parser.add_argument(
        "--fraud-threshold-sec",
        type=int,
        default=3600
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    subscribers = load_subscribers(args.subscribers)

    cdrs, skipped, total = load_cdrs(args.cdrs)

    if total > 0 and skipped / total > 0.10:
        logging.critical("More than 10% malformed rows.")
        sys.exit(1)

    for cdr in cdrs:

        if cdr["msisdn"] in subscribers:
            subscribers[cdr["msisdn"]].calls.append(cdr)

    suspicious = detect_fraud(
        cdrs,
        args.fraud_threshold_sec
    )

    report = {
        "total_calls": len(cdrs),
        "malformed_rows": skipped,
        "suspicious_calls": suspicious,
        "subscriber_totals": {}
    }

    for sub in subscribers.values():
        report["subscriber_totals"][sub.msisdn] = sub.total_cost()

    write_report(report, args.output)


if __name__ == "__main__":
    print(f"Telecom Billing System started on {datetime.date.today()}")
    main()

    