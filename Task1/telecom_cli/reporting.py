import json


def write_report(report, output_path):

    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)