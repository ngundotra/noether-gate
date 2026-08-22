#!/usr/bin/env python3
"""Search for a spec violation, certify it in Lean, deny if Lean accepts the proof."""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


PREFERRED = ["easy-ledger", "medium-orders", "hard-journal"]


def discover() -> list[str]:
    names = []
    if not EXAMPLES.is_dir():
        return names
    for p in sorted(EXAMPLES.iterdir()):
        if p.is_dir() and (p / "SPEC.md").exists() and (p / "search.py").exists():
            names.append(p.name)
    head = [n for n in PREFERRED if n in names]
    tail = [n for n in names if n not in PREFERRED]
    return head + tail


def load_plugin(example: str):
    path = EXAMPLES / example / "search.py"
    if not path.is_file():
        raise SystemExit(f"unknown example {example!r}. have: {discover()}")
    spec = importlib.util.spec_from_file_location(f"noether_{example.replace('-', '_')}", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def lake_check(lean_dir: Path, extra: Path | None = None) -> int:
    rc = subprocess.call(["lake", "build"], cwd=lean_dir)
    if rc != 0 or extra is None:
        return rc
    return subprocess.call(
        ["lake", "env", "lean", str(extra.relative_to(lean_dir))],
        cwd=lean_dir,
    )


def fixture_cases(plug):
    if hasattr(plug, "bad_cases"):
        return list(plug.bad_cases())
    return [(plug.BAD_IMPL, plug.patch_lean_to_bad)]


def try_one(plug, example: str, lean_dir: Path, impl_path: Path, expect_deny: bool) -> int:
    impl_fn = plug.load_impl(impl_path)
    found = plug.search(impl_fn)

    scratch = lean_dir / "Scratch" / "Violation.lean"
    if scratch.exists():
        scratch.unlink()

    if found is None:
        print(f"Noether Gate [{example}]: no witness in the small search. Building corpus.", flush=True)
        rc = lake_check(lean_dir)
        if rc != 0:
            print(f"Noether Gate [{example}]: corpus failed to build.", flush=True)
            return rc
        if expect_deny:
            print(f"Noether Gate [{example}]: expected a deny, found none.", flush=True)
            return 1
        print(f"Noether Gate [{example}]: no violation proved. Approve.", flush=True)
        return 0

    bullet, witness = found
    print(f"Noether Gate [{example}]: Python found a witness for `{bullet}`: {witness}", flush=True)
    print("Writing a Lean certificate and asking the kernel to accept it.", flush=True)
    path = plug.write_violation(lean_dir, bullet, witness)
    rc = lake_check(lean_dir, path)
    if rc == 0:
        print(f"Noether Gate [{example}]: Lean accepted the violation proof. Deny.", flush=True)
        return 0 if expect_deny else 1
    print(
        f"Noether Gate [{example}]: witness found in Python but Lean rejected the certificate.",
        flush=True,
    )
    print("That usually means the Lean model is out of sync with the implementation.", flush=True)
    return 1


def run_one(example: str, impl: Path | None, expect_deny: bool, use_bad: bool) -> int:
    plug = load_plugin(example)
    ex_dir: Path = EXAMPLES / example
    lean_dir: Path = ex_dir / "lean"
    statements = lean_dir / plug.STATEMENTS
    original = statements.read_text()

    if not use_bad:
        impl_path = impl if impl is not None else ex_dir / plug.DEFAULT_IMPL
        return try_one(plug, example, lean_dir, impl_path, expect_deny)

    rc = 0
    for rel, patcher in fixture_cases(plug):
        patched = patcher(original)
        if patched == original:
            print(f"Noether Gate: patcher was a no-op for {example} / {rel}", flush=True)
            return 1
        try:
            statements.write_text(patched)
            print(
                f"Noether Gate: patched {statements.relative_to(ROOT)} for {rel}.",
                flush=True,
            )
            one = try_one(plug, example, lean_dir, ex_dir / rel, expect_deny)
            if one != 0:
                rc = one
        finally:
            statements.write_text(original)
    return rc


def main() -> int:
    p = argparse.ArgumentParser(description="Noether Gate")
    p.add_argument("--example", help="example directory name under examples/")
    p.add_argument("--all", action="store_true", help="run every discovered example")
    p.add_argument("--list", action="store_true", help="print discovered examples")
    p.add_argument("--impl", type=Path, help="override product implementation")
    p.add_argument(
        "--expect-deny",
        action="store_true",
        help="Exit 0 only if a violation is proved (used by the bad-fixture job).",
    )
    p.add_argument(
        "--use-bad-fixture",
        action="store_true",
        help="Patch Lean Impl to the bad model and search the example's fixtures/bad_*.",
    )
    args = p.parse_args()

    names = discover()
    if args.list:
        for n in names:
            print(n)
        return 0 if names else 1

    if args.example and args.all:
        print("pass only one of --example / --all")
        return 2

    if args.example:
        targets = [args.example]
    elif args.all:
        targets = names
    else:
        print("usage: python3 scripts/gate.py --example <name> | --all")
        print("examples:", ", ".join(names) or "(none)")
        return 2

    rc = 0
    for name in targets:
        print(f"======== {name} ========", flush=True)
        one = run_one(name, args.impl, args.expect_deny, args.use_bad_fixture)
        if one != 0:
            rc = one
    return rc


if __name__ == "__main__":
    sys.exit(main())
