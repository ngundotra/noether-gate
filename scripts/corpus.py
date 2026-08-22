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


def barrel_path(example: str, plug) -> Path:
    return EXAMPLES / example / "lean" / plug.PKG / "Corpus.lean"


def corpus_files(d: Path) -> list[Path]:
    if not d.is_dir():
        return []
    return sorted(p for p in d.glob("*.lean") if p.name != ".gitkeep")


def strip_lean_comments(src: str) -> str:
    """Drop `--` line comments and `/- ... -/` blocks (nested)."""
    out: list[str] = []
    i = 0
    n = len(src)
    depth = 0
    while i < n:
        if depth == 0 and src.startswith("--", i):
            j = src.find("\n", i)
            if j < 0:
                break
            out.append("\n")
            i = j + 1
            continue
        if src.startswith("/-", i):
            depth += 1
            i += 2
            continue
        if depth and src.startswith("-/", i):
            depth = max(0, depth - 1)
            i += 2
            continue
        if depth == 0:
            out.append(src[i])
        i += 1
    return "".join(out)


def mentions_impl(src: str) -> bool:
    return re.search(r"\bImpl\b", strip_lean_comments(src)) is not None


def theorem_names(src: str) -> list[str]:
    return re.findall(r"\b(?:theorem|lemma)\s+([A-Za-z_][A-Za-z0-9_']*)", strip_lean_comments(src))


def has_sorry(src: str) -> bool:
    return re.search(r"\bsorry\b", strip_lean_comments(src)) is not None


def cmd_list(example: str) -> int:
    plug = load_plugin(example)
    d = corpus_dir(example, plug)
    print(f"corpus for {example}  ({plug.PKG}.Corpus)")
    files = corpus_files(d)
    if not files:
        print("  (empty)" if d.is_dir() else "  (missing)")
        return 0 if d.is_dir() else 1
    writer = (EXAMPLES / example / "search.py").read_text()
    for p in files:
        rel = p.relative_to(EXAMPLES / example / "lean")
        mod = plug.PKG + ".Corpus." + p.stem
        names = theorem_names(p.read_text())
        cited = [n for n in names if n in writer]
        flag = "cited" if cited else "uncited"
        print(f"  {p.stem:24}  import {mod}    # {rel}  [{flag}]")
        for n in names:
            mark = "*" if n in writer else " "
            print(f"      {mark} {n}")
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
        f"  Must not mention `Impl`. `lake build` in `examples/{example}/lean` must accept it.\n"
        f"-/\n"
        f"namespace {ns}\n"
        f"\n"
        f"-- theorem {name.replace('-', '_')} : True := trivial\n"
        f"\n"
        f"end {ns}\n"
    )
    barrel = barrel_path(example, plug)
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
    print("Then: python3 scripts/corpus.py check --example " + example)
    return 0


def check_one(example: str) -> int:
    plug = load_plugin(example)
    d = corpus_dir(example, plug)
    barrel = barrel_path(example, plug)
    files = corpus_files(d)
    rc = 0
    print(f"======== {example} ========")
    if not barrel.is_file():
        print(f"missing barrel {barrel.relative_to(ROOT)}")
        return 1
    barrel_text = barrel.read_text()
    imported = set(re.findall(r"import\s+" + re.escape(plug.PKG) + r"\.Corpus\.(\w+)", barrel_text))
    stems = {p.stem for p in files}
    for extra in sorted(imported - stems):
        print(f"barrel imports missing file: {plug.PKG}.Corpus.{extra}")
        rc = 1
    for missing in sorted(stems - imported):
        print(f"file not in barrel: Corpus/{missing}.lean")
        rc = 1
    cited_any = False
    writer = (EXAMPLES / example / "search.py").read_text()
    if f"import {plug.PKG}.Corpus" not in writer:
        print(f"search.py does not import {plug.PKG}.Corpus in a certificate")
        rc = 1
    for p in files:
        src = p.read_text()
        if mentions_impl(src):
            print(f"Corpus/{p.name} mentions Impl (move that fact to Safe.lean)")
            rc = 1
        if has_sorry(src):
            print(f"Corpus/{p.name} contains sorry")
            rc = 1
        names = theorem_names(src)
        if not names:
            print(f"Corpus/{p.name} has no theorem (fill the stub)")
            rc = 1
        if any(n in writer for n in names):
            cited_any = True
        print(f"  {p.stem:24}  {len(names)} lemma(s)")
    if files and not cited_any:
        print("no corpus lemma is cited from search.py")
        rc = 1
    if rc == 0:
        print("ok")
    return rc


def cmd_check(example: str | None, all_examples: bool) -> int:
    if example and all_examples:
        print("pass only one of --example / --all")
        return 2
    names = discover() if all_examples or example is None else [example]
    if example is None and not all_examples:
        print("usage: python3 scripts/corpus.py check --example <name> | --all")
        return 2
    rc = 0
    for name in names:
        one = check_one(name)
        if one != 0:
            rc = one
    return rc


def main() -> int:
    p = argparse.ArgumentParser(description="Noether lemma corpus")
    sub = p.add_subparsers(dest="cmd", required=True)

    ls = sub.add_parser("list", help="show lemmas in an example corpus")
    ls.add_argument("--example", required=True)

    add = sub.add_parser("add-lemma", help="write a stub lemma file")
    add.add_argument("--example", required=True)
    add.add_argument("--name", required=True, help="snake_case or PascalCase module name")

    chk = sub.add_parser("check", help="barrel, no Impl/sorry, stub filled, cert cites corpus")
    chk.add_argument("--example")
    chk.add_argument("--all", action="store_true")

    args = p.parse_args()
    if args.cmd == "list":
        return cmd_list(args.example)
    if args.cmd == "add-lemma":
        return cmd_add(args.example, args.name)
    if args.cmd == "check":
        return cmd_check(args.example, args.all)
    return 2


if __name__ == "__main__":
    sys.exit(main())
