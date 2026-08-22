#!/usr/bin/env python3
"""Grow a per-example Lean lemma corpus. Tiny on purpose."""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def discover() -> list[str]:
    names = []
    if not EXAMPLES.is_dir():
        return names
    for p in sorted(EXAMPLES.iterdir()):
        if p.is_dir() and (p / "SPEC.md").exists() and (p / "search.py").exists():
            names.append(p.name)
    return names


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


def pascal(name: str) -> str:
    parts = re.split(r"[-_]+", name.strip())
    out = "".join(p[:1].upper() + p[1:] for p in parts if p)
    if not out or not out[0].isalpha():
        raise SystemExit(f"bad lemma name {name!r}: need a Lean module ident")
    return out


def corpus_dir(example: str, plug) -> Path:
    return EXAMPLES / example / "lean" / plug.PKG / "Corpus"


def cmd_list(example: str) -> int:
    plug = load_plugin(example)
    d = corpus_dir(example, plug)
    print(f"corpus for {example}  ({plug.PKG}.Corpus)")
    if not d.is_dir():
        print("  (missing)")
        return 1
    files = sorted(p for p in d.glob("*.lean") if p.name != ".gitkeep")
    if not files:
        print("  (empty)")
        return 0
    for p in files:
        rel = p.relative_to(EXAMPLES / example / "lean")
        mod = plug.PKG + ".Corpus." + p.stem
        print(f"  {p.stem:24}  import {mod}    # {rel}")
    return 0


def cmd_add(example: str, name: str) -> int:
    plug = load_plugin(example)
    stem = pascal(name)
    d = corpus_dir(example, plug)
    d.mkdir(parents=True, exist_ok=True)
    dest = d / f"{stem}.lean"
    if dest.exists():
        print(f"already exists: {dest.relative_to(ROOT)}")
        print(f"Import with:  import {plug.PKG}.Corpus.{stem}")
        return 1
    ns = plug.PKG
    dest.write_text(
        f"import {ns}.Statements\n"
        f"\n"
        f"/-!\n"
        f"  Helper lemma stub. Replace the placeholder with one small fact.\n"
        f"  `lake build` in `examples/{example}/lean` must accept it.\n"
        f"-/\n"
        f"namespace {ns}\n"
        f"\n"
        f"-- theorem {name.replace('-', '_')} : True := trivial\n"
        f"\n"
        f"end {ns}\n"
    )
    barrel = EXAMPLES / example / "lean" / plug.PKG / "Corpus.lean"
    import_line = f"import {ns}.Corpus.{stem}\n"
    if barrel.is_file():
        text = barrel.read_text()
        if import_line not in text:
            if text and not text.endswith("\n"):
                text += "\n"
            barrel.write_text(text + import_line)
    else:
        barrel.write_text(import_line)
    print(f"wrote {dest.relative_to(ROOT)}")
    print(f"Import with:  import {plug.PKG}.Corpus.{stem}")
    print(f"Also added that import to {barrel.relative_to(ROOT)}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Noether lemma corpus")
    sub = p.add_subparsers(dest="cmd", required=True)

    ls = sub.add_parser("list", help="show lemmas in an example corpus")
    ls.add_argument("--example", required=True)

    add = sub.add_parser("add-lemma", help="write a stub lemma file")
    add.add_argument("--example", required=True)
    add.add_argument("--name", required=True, help="snake_case or PascalCase module name")

    args = p.parse_args()
    if args.cmd == "list":
        return cmd_list(args.example)
    if args.cmd == "add-lemma":
        return cmd_add(args.example, args.name)
    return 2


if __name__ == "__main__":
    sys.exit(main())
