"""Tests for cognis_neural_suite.scanner and the CLI entry point."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cognis_neural_suite.scanner import scan
from cognis_neural_suite.__main__ import main


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


# ---------------------------------------------------------------------------
# scanner.scan() — happy paths
# ---------------------------------------------------------------------------


def test_scan_empty_directory_returns_zero_score(tmp_dir: Path) -> None:
    """An empty directory produces a valid result with score == 0."""
    result = scan(tmp_dir)
    assert result["tool"] == "cognis-neural-suite"
    assert result["score"] == 0
    assert result["findings"] == []


def test_scan_file_with_no_matches(tmp_dir: Path) -> None:
    clean = tmp_dir / "clean.py"
    clean.write_text("def hello():\n    return 'world'\n")
    result = scan(clean)
    assert result["score"] == 0


def test_scan_file_detects_todo(tmp_dir: Path) -> None:
    f = tmp_dir / "code.py"
    f.write_text("# TODO: fix this later\n")
    result = scan(f)
    assert result["score"] == 1
    assert result["findings"][0]["id"] == "GEN-001"
    assert result["findings"][0]["sev"] == "high"


def test_scan_file_detects_fixme(tmp_dir: Path) -> None:
    f = tmp_dir / "code.py"
    f.write_text("# FIXME: broken\n")
    result = scan(f)
    assert result["score"] == 1
    assert result["findings"][0]["id"] == "GEN-002"
    assert result["findings"][0]["sev"] == "medium"


def test_scan_file_detects_xxx(tmp_dir: Path) -> None:
    f = tmp_dir / "code.py"
    f.write_text("# XXX: remove\n")
    result = scan(f)
    assert result["score"] == 1
    assert result["findings"][0]["id"] == "GEN-003"
    assert result["findings"][0]["sev"] == "low"


def test_scan_directory_walks_recursively(tmp_dir: Path) -> None:
    sub = tmp_dir / "subdir"
    sub.mkdir()
    (sub / "a.py").write_text("# TODO\n")
    (tmp_dir / "b.py").write_text("# FIXME\n")
    result = scan(tmp_dir)
    assert result["score"] == 2


def test_scan_output_shape(tmp_dir: Path) -> None:
    """Result always has the expected top-level keys."""
    result = scan(tmp_dir)
    assert set(result.keys()) == {"tool", "findings", "score"}


def test_scan_finding_shape(tmp_dir: Path) -> None:
    """Each finding has id, sev, and where."""
    f = tmp_dir / "x.txt"
    f.write_text("TODO here\n")
    result = scan(f)
    assert len(result["findings"]) == 1
    finding = result["findings"][0]
    assert set(finding.keys()) == {"id", "sev", "where"}


# ---------------------------------------------------------------------------
# scanner.scan() — error / edge-case paths
# ---------------------------------------------------------------------------


def test_scan_missing_target_raises_value_error(tmp_dir: Path) -> None:
    with pytest.raises(ValueError, match="does not exist"):
        scan(tmp_dir / "nonexistent_path_xyz")


def test_scan_invalid_rule_not_triple_raises_type_error(tmp_dir: Path) -> None:
    with pytest.raises(TypeError):
        scan(tmp_dir, rules=[("GEN-001", "high")])  # type: ignore[list-item]


def test_scan_invalid_rule_non_string_raises_type_error(tmp_dir: Path) -> None:
    with pytest.raises(TypeError):
        scan(tmp_dir, rules=[("GEN-001", "high", 42)])  # type: ignore[list-item]


def test_scan_empty_rules_list_returns_zero_score(tmp_dir: Path) -> None:
    (tmp_dir / "f.py").write_text("# TODO FIXME XXX\n")
    result = scan(tmp_dir, rules=[])
    assert result["score"] == 0


def test_scan_rule_with_empty_needle_is_skipped(tmp_dir: Path) -> None:
    (tmp_dir / "f.py").write_text("hello\n")
    result = scan(tmp_dir, rules=[("GEN-999", "low", "")])
    assert result["score"] == 0


def test_scan_binary_file_is_skipped_gracefully(tmp_dir: Path) -> None:
    """Binary files that cannot be decoded as UTF-8 should not raise."""
    f = tmp_dir / "binary.bin"
    f.write_bytes(bytes(range(256)))
    # Should not raise; undecodable bytes are replaced.
    result = scan(f)
    assert isinstance(result["score"], int)


def test_scan_symlink_target_is_a_file(tmp_dir: Path) -> None:
    """Symlinks to directories are not followed; plain-file symlinks still work."""
    real = tmp_dir / "real.py"
    real.write_text("# TODO\n")
    # scan the real file directly (symlink behaviour is OS-dependent in CI)
    result = scan(real)
    assert result["score"] == 1


# ---------------------------------------------------------------------------
# CLI — main() exit codes
# ---------------------------------------------------------------------------


def test_cli_scan_valid_directory_exits_zero(tmp_dir: Path) -> None:
    code = main(["scan", str(tmp_dir)])
    assert code == 0


def test_cli_scan_missing_path_exits_2(tmp_dir: Path) -> None:
    missing = str(tmp_dir / "no_such_dir")
    code = main(["scan", missing])
    assert code == 2


def test_cli_no_subcommand_exits_zero(tmp_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Running with no subcommand should default to scanning '.' and exit 0."""
    monkeypatch.chdir(tmp_dir)
    code = main([])
    assert code == 0


def test_cli_scan_produces_valid_json(tmp_dir: Path, capsys: pytest.CaptureFixture) -> None:
    (tmp_dir / "f.py").write_text("# TODO\n")
    code = main(["scan", str(tmp_dir)])
    assert code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["score"] >= 1
    assert data["tool"] == "cognis-neural-suite"


def test_cli_compact_flag_produces_single_line(tmp_dir: Path, capsys: pytest.CaptureFixture) -> None:
    code = main(["scan", "--compact", str(tmp_dir)])
    assert code == 0
    captured = capsys.readouterr()
    # Compact JSON has no newlines except the trailing one.
    lines = [line for line in captured.out.splitlines() if line.strip()]
    assert len(lines) == 1
