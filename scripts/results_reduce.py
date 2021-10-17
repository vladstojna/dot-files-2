#!/usr/bin/env python3

import argparse
import json
import sys
import statistics
from typing import Any, Callable, Dict


def read_from(path):
    return sys.stdin if not path else open(path, "r")


def output_to(path):
    return sys.stdout if not path else open(path, "w")


operations: Dict[str, Callable] = {
    "max": lambda x: max(x),
    "mix": lambda x: min(x),
    "avg": lambda x: statistics.mean(x),
    "median": lambda x: statistics.median(x),
    "sum": lambda x: sum(x),
}


def add_arguments(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument(
        "source_file",
        action="store",
        help="file to reduce (default: stdin)",
        nargs="?",
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
    parser.add_argument(
        "--op",
        action="store",
        help="which reduction operation to apply",
        required=True,
        choices=operations,
    )

    parser.add_argument(
        "--op-time",
        action="store",
        help="""which reduction operation to apply to time measurements
            (default: avg)""",
        required=False,
        choices=operations,
        default="avg",
    )
    return parser


def apply_operation(metric: Dict, args: Any) -> None:
    if not isinstance(metric["value"], list):
        return
    lower = metric["measurement"].lower()
    if "time" in lower or "latency" in lower:
        metric["value"] = operations[args.op_time](metric["value"])
    else:
        metric["value"] = operations[args.op](metric["value"])


def main():
    parser = argparse.ArgumentParser(description="Reduce YCSB JSON values")
    args = add_arguments(parser).parse_args()
    with read_from(args.source_file) as sf:
        json_in = json.load(sf)
        for m in json_in:
            apply_operation(m, args)
        with output_to(args.output) as of:
            json.dump(json_in, of)


if __name__ == "__main__":
    main()
