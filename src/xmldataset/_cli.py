"""The ``xmldataset`` command-line tool."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import xml.etree.ElementTree as ET
from collections.abc import Sequence
from pathlib import Path
from typing import IO, Any

from . import __version__
from ._api import iter_records, json_schema, parse_using_profile
from ._engine import check_references
from ._errors import MissingProcessError, XMLDatasetError
from ._structured import load_profile


def _pairs(values: list[str] | None, option: str) -> dict[str, str]:
    out = {}
    for item in values or []:
        key, sep, value = item.partition("=")
        if not sep or not key:
            raise SystemExit(
                f"xmldataset: error: {option} expects KEY=VALUE, got {item!r}"
            )
        out[key] = value
    return out


def _xml_source(path: str) -> Any:
    return sys.stdin.buffer if path == "-" else Path(path)


def _open_output(path: str | None) -> IO[str]:
    return open(path, "w", encoding="utf-8", newline="") if path else sys.stdout


def _run(args: argparse.Namespace) -> None:
    profile = load_profile(args.profile)
    options: dict[str, Any] = {
        "namespaces": _pairs(args.namespace, "--namespace") or None,
        "global_values": _pairs(args.global_value, "--global") or None,
    }
    source = _xml_source(args.xml)
    out = _open_output(args.output)
    try:
        if args.format == "json":
            result = parse_using_profile(source, profile, **options)
            if args.dataset:
                result = {args.dataset: result.get(args.dataset, [])}
            json.dump(result, out, indent=2, ensure_ascii=False)
            out.write("\n")
        elif args.format == "jsonl":
            for dataset, record in iter_records(source, profile, **options):
                if args.dataset is None or dataset == args.dataset:
                    out.write(
                        json.dumps(
                            {"dataset": dataset, "record": record}, ensure_ascii=False
                        )
                        + "\n"
                    )
        else:
            dataset = args.dataset
            if dataset is None:
                if len(profile.datasets) != 1:
                    raise SystemExit(
                        "xmldataset: error: --format csv needs --dataset;"
                        " the profile has"
                        f" datasets {', '.join(profile.datasets) or '(none)'}"
                    )
                dataset = profile.datasets[0]
            rows = [
                r for d, r in iter_records(source, profile, **options) if d == dataset
            ]
            columns: dict[str, None] = {}
            for row in rows:
                columns.update(dict.fromkeys(row))
            writer = csv.DictWriter(out, fieldnames=list(columns))
            writer.writeheader()
            for row in rows:
                writer.writerow(
                    {
                        k: json.dumps(v, ensure_ascii=False)
                        if isinstance(v, list)
                        else v
                        for k, v in row.items()
                    }
                )
    finally:
        if out is not sys.stdout:
            out.close()


def _convert(args: argparse.Namespace) -> None:
    profile = load_profile(args.profile)
    text = {"dsl": profile.to_dsl, "yaml": profile.to_yaml, "json": profile.to_json}[
        args.to
    ]()
    out = _open_output(args.output)
    try:
        out.write(text)
    finally:
        if out is not sys.stdout:
            out.close()


def _validate(args: argparse.Namespace) -> int:
    failed = False
    for path in args.profiles:
        try:
            profile = load_profile(path)
            check_references(profile)
        except XMLDatasetError as exc:
            print(f"{path}: {exc}", file=sys.stderr)
            failed = True
        else:
            datasets = ", ".join(profile.datasets) or "no datasets"
            print(f"{path}: ok ({datasets})")
    return 1 if failed else 0


def _schema(args: argparse.Namespace) -> None:
    print(json.dumps(json_schema(), indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xmldataset",
        description="Extract datasets from XML using a profile (text, YAML or JSON).",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    commands = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    run = commands.add_parser("run", help="extract datasets from an XML file")
    run.add_argument("profile", help="profile file (.yaml/.yml, .json, or text syntax)")
    run.add_argument("xml", help="XML file, or - for standard input")
    run.add_argument(
        "-f",
        "--format",
        choices=["json", "jsonl", "csv"],
        default="json",
        help="output format (default: json)",
    )
    run.add_argument(
        "-d",
        "--dataset",
        help="only output this dataset (required for csv when the profile has several)",
    )
    run.add_argument(
        "-n",
        "--namespace",
        action="append",
        metavar="PREFIX=URI",
        help="namespace prefix used in the profile (repeatable)",
    )
    run.add_argument(
        "-g",
        "--global",
        dest="global_value",
        action="append",
        metavar="KEY=VALUE",
        help="value added to every record (repeatable)",
    )
    run.add_argument(
        "-o", "--output", help="write to this file instead of standard output"
    )
    run.set_defaults(handler=_run)

    convert = commands.add_parser(
        "convert", help="convert a profile between text, YAML and JSON"
    )
    convert.add_argument(
        "profile", help="profile file (.yaml/.yml, .json, or text syntax)"
    )
    convert.add_argument(
        "-t",
        "--to",
        choices=["dsl", "yaml", "json"],
        default="yaml",
        help="output format (default: yaml)",
    )
    convert.add_argument(
        "-o", "--output", help="write to this file instead of standard output"
    )
    convert.set_defaults(handler=_convert)

    validate = commands.add_parser("validate", help="check profiles for errors")
    validate.add_argument("profiles", nargs="+", metavar="profile")
    validate.set_defaults(handler=_validate)

    schema = commands.add_parser(
        "schema", help="print the JSON Schema for YAML/JSON profiles"
    )
    schema.set_defaults(handler=_schema)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command line; returns the exit status."""
    args = build_parser().parse_args(argv)
    try:
        status: int | None = args.handler(args)
    except MissingProcessError as exc:
        print(
            f"xmldataset: error: {exc}"
            " (process functions can only be supplied from Python)",
            file=sys.stderr,
        )
        return 1
    except (XMLDatasetError, ET.ParseError, OSError, ImportError) as exc:
        print(f"xmldataset: error: {exc}", file=sys.stderr)
        return 1
    return status or 0


__all__ = ["build_parser", "main"]
