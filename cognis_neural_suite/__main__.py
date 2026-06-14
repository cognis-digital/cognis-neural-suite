"""CLI entry point: ``python -m cognis_neural_suite`` or ``cognis-neural-suite``."""

from __future__ import annotations

import argparse
import json
import sys

from cognis_neural_suite.scanner import DEFAULT_RULES, scan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cognis-neural-suite",
        description=(
            "Scan a directory or file for code-smell patterns "
            "(TODO/FIXME/XXX) and emit a JSON report."
        ),
    )
    sub = parser.add_subparsers(dest="command")

    scan_cmd = sub.add_parser("scan", help="Scan a target path.")
    scan_cmd.add_argument(
        "target",
        nargs="?",
        default=".",
        help="File or directory to scan (default: current directory).",
    )
    scan_cmd.add_argument(
        "--pretty",
        action="store_true",
        default=True,
        help="Pretty-print the JSON output (default: on).",
    )
    scan_cmd.add_argument(
        "--compact",
        action="store_true",
        default=False,
        help="Emit compact (single-line) JSON instead of pretty-printed.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point.  Returns an exit code (0 = success, non-zero = error)."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        # No subcommand: default to scanning the current directory (mirrors
        # the JS/Go/Rust ports that accept a bare path argument).
        target = "."
        pretty = True
    elif args.command == "scan":
        target = args.target
        pretty = not args.compact
    else:
        parser.print_help(sys.stderr)
        return 2

    try:
        result = scan(target, DEFAULT_RULES)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except PermissionError as exc:
        print(f"error: permission denied — {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"error: unexpected failure — {exc}", file=sys.stderr)
        return 1

    indent = 2 if pretty else None
    try:
        print(json.dumps(result, indent=indent))
    except (BrokenPipeError, OSError):
        # Caller closed the pipe (e.g. `| head`); exit cleanly.
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
