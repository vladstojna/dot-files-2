#!/usr/bin/env python3

import argparse
import json
import sys
import csv
from typing import Dict, List, Union


def read_from(path):
    return sys.stdin if not path else open(path, "r")


def output_to(path):
    return sys.stdout if not path else open(path, "w", newline="")


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
        "--sep",
        action="store",
        help="fieldname domain separator (default: @)",
        required=False,
        type=str,
        default="@",
    )
    return parser


def metric2fieldname(m: Dict, sep: str) -> str:
    return "{}{}{}".format(m["measurement"], sep, m["metric"])


def main():
    parser = argparse.ArgumentParser(description="Reduce YCSB JSON values")
    args = add_arguments(parser).parse_args()
    with read_from(args.source_file) as sf:
        json_in = json.load(sf)
        fieldnames: List[str] = [
            "count",
            *(metric2fieldname(m, args.sep) for m in json_in),
        ]
        rows: List[List[Union[int, float]]] = []
        for x in range(0, len(json_in[0]["value"])):
            rows.append([x, *(m["value"][x] for m in json_in)])
        with output_to(args.output) as of:
            writer = csv.writer(of)
            writer.writerow(fieldnames)
            writer.writerows(rows)


if __name__ == "__main__":
    main()
