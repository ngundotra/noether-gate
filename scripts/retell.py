#!/usr/bin/env python3
"""Print a human-readable retelling card for an example. Not a proof."""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def spec_bullets(example: str) -> list[str]:
    text = (ROOT / "examples" / example / "SPEC.md").read_text()
    lines = []
    for raw in text.splitlines():
        s = raw.strip()
        if s.startswith("|") and "Bullet" not in s and not s.startswith("|---"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) >= 2 and cells[0] and cells[0] != "id":
                lines.append(f"{cells[0]}: {cells[1]}")
    return lines


def card(example: str, ending: str) -> str:
    bullets = spec_bullets(example)
    body = "\n".join(f"- {b}" for b in bullets) or "- (no bullets found)"
    if ending == "match":
        verdict = "still matches — the old rules still hold"
    else:
        verdict = "rules changed — this PR is updating the contract"
    return (
        f"## Retelling of `{example}`\n\n"
        f"This is the understanding we would check in. "
        f"If you do not agree with these lines, stop.\n\n"
        f"{body}\n\n"
        f"**Ending:** {verdict}\n"
    )


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--example", default="easy-ledger")
    p.add_argument("--ending", choices=("match", "update"), default="match")
    args = p.parse_args()
    print(card(args.example, args.ending))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
