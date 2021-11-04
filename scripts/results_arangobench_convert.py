#!/usr/bin/env python3

import argparse
import json
import sys
import csv
from typing import Any, Dict, Iterable, List


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


def metrics2fieldnames(metrics: Dict) -> List[List[str]]:
    def _generate_fieldname(lst, current, values: Any) -> List[List[str]]:
        if isinstance(values, list):
            lst.append(current)
        else:
            for k, v in values.items():
                _generate_fieldname(lst, current + [k], v)
        return lst

    return _generate_fieldname([], [], metrics)


def metrics2values(metrics: Dict) -> List[List[Any]]:
    def _generate_values(lst, current, values: Any) -> List[List[Any]]:
        if isinstance(values, list):
            lst.append(values)
        else:
            for v in values.values():
                _generate_values(lst, current + [v], v)
        return lst

    return _generate_values([], [], metrics)


def assert_extra_fields(extra: Iterable[field_values], count: int) -> None:
    for e in extra:
        if len(e.values) != count:
            raise ValueError("Extra fields must have exactly {} values".format(count))


def main():
    parser = argparse.ArgumentParser(
        description="Convert arangobench JSON output to CSV"
    )
    args = add_arguments(parser).parse_args()
    with read_from(args.source_file) as sf:
        json_in: Dict = json.load(sf)

        # total number of operations should always exist,
        # get the default value count from it
        count = len(json_in["totalNumberOfOperations"])
        assert_extra_fields(args.extra, count)

        fieldnames: List[str] = [
            "count",
            *(x.fieldname for x in args.extra),
            *(args.sep.join(f) for f in metrics2fieldnames(json_in)),
        ]
        rows: List[List[Any]] = []

        values = metrics2values(json_in)
        for x in range(0, count):
            rows.append(
                [
                    x,
                    *(fv.values[x] for fv in args.extra),
                    *(v[x] if x < len(v) else "" for v in values),
                ]
            )
        with output_to(args.output) as of:
            writer = csv.writer(of)
            writer.writerow(fieldnames)
            writer.writerows(rows)


if __name__ == "__main__":
    main()
