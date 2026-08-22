#!/usr/bin/env python3
"""Check that a PR's Lean contract is present, accepted, finished, and consistent."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

BARREL_NAME = "Retellings.lean"
DEFAULT_DIR = Path("plugin/retellings")

EXEMPT_PREFIXES = (
    "docs/",
    ".github/",
)
EXEMPT_FILES = {
    "LICENSE",
    "README.md",
    "AGENTS.md",
    "scripts/check_contract.py",
    "plugin/README.md",
    "plugin/retellings/lakefile.toml",
    "plugin/retellings/lean-toolchain",
    "plugin/retellings/lake-manifest.json",
}
EXEMPT_SUFFIXES = (
    "plugin/retellings/lakefile.toml",
    "plugin/retellings/lean-toolchain",
    "plugin/retellings/lake-manifest.json",
)

SORRY_RE = re.compile(r"\b(?:sorry|admit)\b")
FALSE_DECL_RE = re.compile(
    r"(?m)^\s*(?:theorem|example|def|lemma)\s+(\S+)\s*:\s*(.*?)\s*:=",
    re.S,
)
DECL_BY_EOL_RE = re.compile(
    r"^\s*(?:theorem|example|lemma)\b.*:=\s*by\s*$"
)


def normalize_path(path: str) -> str:
    path = path.strip().replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    return path


def is_contract_lean_path(path: str) -> bool:
    path = normalize_path(path)
    if not path.startswith("plugin/retellings/") or not path.endswith(".lean"):
        return False
    rest = path[len("plugin/retellings/") :]
    return "/" not in rest and rest != ""


def is_exempt_path(path: str) -> bool:
    path = normalize_path(path)
    if not path:
        return True
    if path in EXEMPT_FILES:
        return True
    if any(path.startswith(prefix) for prefix in EXEMPT_PREFIXES):
        return True
    if path.startswith("plugin/retellings/") and path.endswith(".md"):
        return True
    if any(path.endswith(suffix) if suffix.startswith("/") else path == suffix for suffix in EXEMPT_SUFFIXES):
        return True
    return False


def all_exempt(paths: list[str]) -> bool:
    changed = [normalize_path(p) for p in paths if normalize_path(p)]
    return bool(changed) and all(is_exempt_path(p) for p in changed) or not changed


def strip_comments(src: str) -> str:
    src = re.sub(r"/-.*?-/", lambda m: "\n" * m.group(0).count("\n"), src, flags=re.S)
    src = re.sub(r"--[^\n]*", "", src)
    return src


def unfinished_reasons(src: str) -> list[str]:
    body = strip_comments(src)
    reasons: list[str] = []
    if SORRY_RE.search(body):
        reasons.append("unfinished proof (sorry or admit)")
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if not DECL_BY_EOL_RE.match(line):
            continue
        rest = lines[i + 1 :]
        j = 0
        while j < len(rest) and not rest[j].strip():
            j += 1
        if j >= len(rest) or not rest[j].startswith((" ", "\t")):
            reasons.append("unfinished proof (empty proof)")
            break
    return reasons


def contradiction_names(src: str) -> list[str]:
    body = strip_comments(src)
    names: list[str] = []
    for match in FALSE_DECL_RE.finditer(body):
        typ = re.sub(r"\s+", " ", match.group(2)).strip()
        if typ == "False":
            names.append(match.group(1))
    return names


def contract_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.glob("*.lean") if p.is_file())


def non_barrel_contracts(directory: Path) -> list[Path]:
    return [p for p in contract_files(directory) if p.name != BARREL_NAME]


def read_pr_files(spec: str) -> list[str]:
    if spec == "-":
        return [normalize_path(line) for line in sys.stdin.read().splitlines() if normalize_path(line)]
    path = Path(spec)
    text = path.read_text(encoding="utf-8")
    return [normalize_path(line) for line in text.splitlines() if normalize_path(line)]


def lean_build(pkg: Path) -> tuple[int, str]:
    env = os.environ.copy()
    elan = str(Path.home() / ".elan" / "bin")
    env["PATH"] = elan + os.pathsep + env.get("PATH", "")
    try:
        proc = subprocess.run(
            ["lake", "build"],
            cwd=pkg,
            env=env,
            capture_output=True,
            text=True,
            timeout=300,
        )
    except FileNotFoundError:
        return 1, "Lean rejected the file: lake is not on PATH"
    except subprocess.TimeoutExpired:
        return 1, "Lean rejected the file: lake build timed out"
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "lake build failed").strip()
        lines = detail.splitlines()
        tail = "\n".join(lines[-25:]) if lines else "lake build failed"
        return 1, f"Lean rejected the file\n{tail}"
    return 0, "Lean accepted the contracts"


def scan_contracts(directory: Path) -> list[str]:
    problems: list[str] = []
    files = contract_files(directory)
    if not files:
        return ["contract missing"]
    for path in files:
        src = path.read_text(encoding="utf-8")
        for reason in unfinished_reasons(src):
            problems.append(f"{path}: {reason}")
        for name in contradiction_names(src):
            problems.append(f"{path}: contradiction ({name} proves False)")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Lean contracts for a PR.")
    parser.add_argument(
        "--pr-files",
        metavar="FILE",
        help="Changed paths (one per line). Use - to read stdin.",
    )
    parser.add_argument(
        "--dir",
        default=str(DEFAULT_DIR),
        help="Directory of contract .lean files (default: plugin/retellings).",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip lake build (text checks only).",
    )
    args = parser.parse_args()
    directory = Path(args.dir)

    if args.pr_files is not None:
        changed = read_pr_files(args.pr_files)
        if not all_exempt(changed):
            touched_contract = any(is_contract_lean_path(p) for p in changed)
            if not touched_contract or not non_barrel_contracts(directory):
                print("contract missing")
                print("Every product change needs a Lean contract in plugin/retellings/.")
                return 1

    if not args.skip_build:
        lakefile = directory / "lakefile.toml"
        if lakefile.is_file():
            code, message = lean_build(directory)
            if code != 0:
                print(message)
                return 1
        elif directory.is_dir() and any(directory.glob("lakefile.*")):
            code, message = lean_build(directory)
            if code != 0:
                print(message)
                return 1

    problems = scan_contracts(directory)
    if problems:
        if any("unfinished" in item for item in problems):
            print("unfinished proof")
        elif any("contradiction" in item for item in problems):
            print("contradiction")
        else:
            print(problems[0])
        for item in problems:
            print(item)
        return 1

    files = non_barrel_contracts(directory) or contract_files(directory)
    names = ", ".join(p.name for p in files) or "none"
    print(f"Contracts ok: {names}. Lean accepted them; nothing unfinished; no contradiction.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
