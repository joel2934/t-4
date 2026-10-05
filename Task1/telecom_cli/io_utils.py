import csv
import json
import logging

from models import Subscriber


def parse_cdr_line(row: dict) -> dict:

    required = ["msisdn", "call_type", "duration_sec"]

    for field in required:
        if field not in row:
            raise ValueError(f"Missing required field: {field}")

    try:
        duration = int(row["duration_sec"])
    except ValueError:
        raise ValueError("duration_sec must be an integer")

    return {
        "msisdn": row["msisdn"].strip(),
        "call_type": row["call_type"].strip().lower(),
        "duration_sec": duration
    }


def parse_legacy_line(line: str):

    parts = line.strip().split("|")

    if len(parts) != 3:
        raise ValueError("Invalid legacy record")

    return {
        "msisdn": parts[0].strip(),
        "call_type": parts[1].strip().lower(),
        "duration_sec": int(parts[2].strip())
    }


def load_subscribers(json_path):

    with open(json_path, "r") as f:
        data = json.load(f)

    subscribers = {}

    for item in data:
        subscribers[item["msisdn"]] = Subscriber(
            item["msisdn"],
            item["plan_type"]
        )

    return subscribers


def load_cdrs(csv_path):

    records = []
    skipped = 0
    total = 0

    with open(csv_path, newline="") as f:

        reader = csv.DictReader(f)

        for row in reader:

            total += 1

            try:
                records.append(parse_cdr_line(row))
            except ValueError as e:
                skipped += 1
                logging.warning(e)

    return records, skipped, total