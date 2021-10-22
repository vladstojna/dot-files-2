#!/usr/bin/env python3

import argparse
import json
import sys
import csv
from typing import Any, Dict, Iterable, List, Union


def log(*args: Any) -> None:
    print("{}:".format(sys.argv[0]), *args, file=sys.stderr)


def read_from(path):
    return sys.stdin if not path else open(path, "r", encoding="utf-8")


def output_to(path):
    if not path:
        return sys.stdout
    return open(path, "w", newline="", encoding="utf-8")


class field_values:
    def __init__(self, x: str) -> None:
        self._str2field(x)

    def _str2field(self, x: str):
        self.fieldname, _, value = x.partition("=")
        if not self.fieldname:
            raise argparse.ArgumentTypeError("FIELDNAME cannot be empty")
        if not value:
            raise argparse.ArgumentTypeError("VALUE list cannot be empty")
        self.values = value.split(",")
        for v in self.values:
            if not v:
                raise argparse.ArgumentTypeError("VALUE cannot be empty")

    def __str__(self) -> str:
        return "{{ {}: {} }}".format(self.fieldname, self.values)

    def __repr__(self):
        return str(self)


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
        help="fieldname domain separator (default: /)",
        required=False,
        type=str,
        default="/",
    )
    parser.add_argument(
        "--extra",
        action="append",
        help="add an extra fieldname/column with values",
        required=False,
        type=field_values,
        metavar="FIELDNAME=VALUE[,VALUE ...]",
        default=[],
    )
    return parser


def metric2fieldname(m: Dict, sep: str) -> str:
    return "{}{}{}".format(m["metric"], sep, m["measurement"])


def assert_extra_fields(extra: Iterable[field_values], count: int) -> None:
    for e in extra:
        if len(e.values) != count:
            raise ValueError("Extra fields must have exactly {} values".format(count))


def find_metric(metrics: List, metric: str, measurement: str) -> Dict:
    found = next(
        filter(
            lambda x: x["metric"] == metric and x["measurement"] == measurement, metrics
        ),
        None,
    )
    if found is None:
        raise ValueError(
            "Metric {} with measurement {} not found".format(metric, measurement)
        )
    return found


def candidate(metric: Dict, count: int, quiet: bool = True) -> bool:
    if len(metric["value"]) == count:
        return True
    if not quiet:
        log("Leaving out metric", metric2fieldname(metric, " in "))
    return False


def main():
    parser = argparse.ArgumentParser(description="Reduce YCSB JSON values")
    args = add_arguments(parser).parse_args()
    with read_from(args.source_file) as sf:
        json_in = json.load(sf)

        # Overall runtime should always exist,
        # get the default value count from it
        overall_runtime = find_metric(json_in, "OVERALL", "RunTime(ms)")
        count = len(overall_runtime["value"])

        assert_extra_fields(args.extra, count)

        fieldnames: List[str] = [
            "count",
            *(x.fieldname for x in args.extra),
            *(
                metric2fieldname(m, args.sep)
                for m in json_in
                if candidate(m, count, quiet=False)
            ),
        ]
        rows: List[List[Union[int, float]]] = []

        for x in range(0, count):
            rows.append(
                [
                    x,
                    *(fv.values[x] for fv in args.extra),
                    *(m["value"][x] for m in json_in if candidate(m, count)),
                ]
            )
        with output_to(args.output) as of:
            writer = csv.writer(of)
            writer.writerow(fieldnames)
            writer.writerows(rows)


if __name__ == "__main__":
    main()
