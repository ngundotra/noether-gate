#!/usr/bin/env python3
"""Ask Cursor to start a cloud agent that retells this PR in Lean."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.cursor.com/v1/agents"
REPO = "https://github.com/ngundotra/noether-gate"


def main() -> int:
    key = os.environ.get("CURSOR_API_KEY", "").strip()
    if not key:
        print("CURSOR_API_KEY is not set. Add it as a GitHub Actions secret.")
        print("Make one at https://cursor.com/dashboard/api")
        return 2

    pr_url = os.environ.get("PR_URL", "").strip()
    pr_num = os.environ.get("PR_NUMBER", "").strip()
    sha = os.environ.get("HEAD_SHA", "").strip()
    if not pr_url and pr_num:
        pr_url = f"{REPO}/pull/{pr_num}"

    prompt = f"""A PR landed on noether-gate. Retell THIS change in Lean.

PR: {pr_url or '(no PR url)'}
head: {sha or 'unknown'}

Do this:
1. Read the PR diff. Read any SPEC.md next to the changed code.
2. Write plugin/retellings/pr-{pr_num or 'local'}.md in plain language a person can review:
   - what the change is allowed to do
   - what it must never do
   - ending: "still matches" (old rules hold) or "rules changed" (the contract itself moved)
3. Write a short Lean file under the matching example (or plugin/retellings/) that states those rules. No sorry. Do not mention a second copy of the program if you can state the rules as properties.
4. If Lean can show the old rules still hold, say so. If the PR is changing the rules, show the old vs new contract. If you can prove a rule is now broken, say DENY and show the case.
5. Open or update a PR with only those retelling files, or push onto this PR if you are already on it.

Stay in this repo. The retelling is the thing a human reviews, not the raw diff.
"""

    repo_entry = {"url": REPO}
    if pr_url:
        repo_entry["prUrl"] = pr_url
    body = {
        "name": f"Retell PR {pr_num or sha or 'change'}"[:100],
        "prompt": {"text": prompt},
        "repos": [repo_entry],
        "autoCreatePR": False,
        "workOnCurrentBranch": True,
    }

    req = urllib.request.Request(
        API,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    # Basic auth: key as username, empty password
    import base64

    token = base64.b64encode(f"{key}:".encode()).decode()
    req.add_header("Authorization", f"Basic {token}")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err = e.read().decode(errors="replace")
        print(f"Cursor API {e.code}: {err}", file=sys.stderr)
        return 1

    agent = data.get("agent") or data
    url = agent.get("url") or f"https://cursor.com/agents/{agent.get('id')}"
    print(f"spawned {agent.get('id')}")
    print(url)
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"agent_id={agent.get('id','')}\n")
            f.write(f"agent_url={url}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
