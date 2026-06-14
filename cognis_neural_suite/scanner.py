"""Core scan logic for cognis-neural-suite.

Walk a directory (or single file), apply text-pattern rules, and return a
structured result dict that matches the shared JSON output shape used by the
JS/Go/Rust ports.

Output shape:
    {
        "tool": "cognis-neural-suite",
        "findings": [{"id": str, "sev": str, "where": str}, ...],
        "score": int
    }
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

# Each rule is (rule_id, severity, needle).
# Needle matching is case-sensitive to avoid false positives.
DEFAULT_RULES: list[tuple[str, str, str]] = [
    ("GEN-001", "high", "TODO"),
    ("GEN-002", "medium", "FIXME"),
    ("GEN-003", "low", "XXX"),
]

# Files larger than this are skipped to avoid memory pressure.
_MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MB


def _walk(path: Path) -> Iterator[Path]:
    """Yield all regular files under *path* (or *path* itself if it is a file).

    Silently skips entries that cannot be stat'd (permission errors, broken
    symlinks, race conditions).
    """
    try:
        if path.is_file():
            yield path
            return
        if not path.is_dir():
            return
        for entry in os.scandir(path):
            try:
                entry_path = Path(entry.path)
                if entry.is_dir(follow_symlinks=False):
                    yield from _walk(entry_path)
                elif entry.is_file(follow_symlinks=False):
                    yield entry_path
            except OSError:
                continue
    except OSError:
        return


def scan(
    target: str | os.PathLike[str],
    rules: list[tuple[str, str, str]] | None = None,
) -> dict:
    """Scan *target* (file or directory) with *rules*.

    Parameters
    ----------
    target:
        Path to scan.  May be a file or directory.  Must exist.
    rules:
        List of ``(rule_id, severity, needle)`` triples.  Defaults to
        :data:`DEFAULT_RULES`.

    Returns
    -------
    dict
        ``{"tool": "cognis-neural-suite", "findings": [...], "score": int}``

    Raises
    ------
    ValueError
        If *target* does not exist.
    TypeError
        If *rules* contains entries that are not 3-tuples of strings.
    """
    target_path = Path(target)
    if not target_path.exists():
        raise ValueError(f"Target does not exist: {target_path}")

    if rules is None:
        rules = DEFAULT_RULES

    # Validate rules structure early so callers get a clear error.
    for i, rule in enumerate(rules):
        if not (isinstance(rule, (list, tuple)) and len(rule) == 3):
            raise TypeError(
                f"Rule at index {i} must be a 3-element sequence (id, severity, needle); "
                f"got {rule!r}"
            )
        if not all(isinstance(part, str) for part in rule):
            raise TypeError(
                f"Rule at index {i}: all parts must be strings; got {rule!r}"
            )

    findings: list[dict] = []

    for filepath in _walk(target_path):
        # Skip files that are too large.
        try:
            if filepath.stat().st_size > _MAX_FILE_BYTES:
                continue
        except OSError:
            continue

        # Read as text; skip binary/undecodable files gracefully.
        try:
            text = filepath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        for rule_id, severity, needle in rules:
            if not needle:
                continue
            if needle in text:
                findings.append({"id": rule_id, "sev": severity, "where": str(filepath)})

    return {
        "tool": "cognis-neural-suite",
        "findings": findings,
        "score": len(findings),
    }
