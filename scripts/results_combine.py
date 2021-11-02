#!/usr/bin/env python3

import argparse
import json
import sys
from typing import Any, Dict, Iterable


def output_to(path):
    return sys.stdout if not path else open(path, "w", encoding="utf-8")


def add_arguments(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument(
        "source_file",
        action="store",
        help="files to combine",
        nargs="+",
        type=str,
    )
    parser.add_argument(
        "-o",
        "--output",
        action="store",
        help="destination file (default: stdout)",
        required=False,
        type=str,
        default=None,
    )
    return parser


def load_json_files(files: Iterable[str]) -> Iterable:
    retval = []
    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            retval.append(json.load(f))
    return retval


def equal_metrics(x, y) -> bool:
    return x["metric"] == y["metric"] and x["measurement"] == y["measurement"]


def add_metric(json_out: Any, metric: Dict) -> None:
    found = next(filter(lambda x: equal_metrics(x, metric), json_out), None)
    if found is None:
        json_out.append(
            {
                "metric": metric["metric"],
                "measurement": metric["measurement"],
                "value": [metric["value"]],
            }
        )
    else:
        found["value"].append(metric["value"])


def main():
    parser = argparse.ArgumentParser(description="Combine multiple YCSB JSON outputs")
    args = add_arguments(parser).parse_args()
    json_inputs = load_json_files(args.source_file)
    json_out = []
    for json_in in json_inputs:
        for metric in json_in:
            add_metric(json_out, metric)
    with output_to(args.output) as f:
        json.dump(json_out, f)


if __name__ == "__main__":
    main()
