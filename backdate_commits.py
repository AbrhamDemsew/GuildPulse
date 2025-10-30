"""Rewrite all commit dates evenly across Aug–Oct 2025 using git-filter-repo."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent
TZ = timezone(timedelta(hours=3))
START = datetime(2025, 8, 1, 9, 15, 0, tzinfo=TZ)
END = datetime(2025, 10, 31, 17, 45, 0, tzinfo=TZ)
DATE_MAP = REPO / ".date-map.json"


def run(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def main() -> None:
    commits = run("rev-list", "--reverse", "HEAD").splitlines()
    n = len(commits)
    step = (END - START) / (n - 1) if n > 1 else timedelta(0)

    dates: dict[str, str] = {}
    for i, sha in enumerate(commits):
        when = START + step * i
        ts = int(when.timestamp())
        dates[sha] = f"{ts} +0300"

    DATE_MAP.write_text(json.dumps(dates, indent=2), encoding="utf-8")

    callback = (
        "import json\n"
        "from pathlib import Path\n"
        "dates = json.loads(Path('.date-map.json').read_text(encoding='utf-8'))\n"
        'oid = commit.original_id.decode("ascii")\n'
        "if oid in dates:\n"
        "    commit.author_date = dates[oid].encode()\n"
        "    commit.committer_date = dates[oid].encode()\n"
        "return commit\n"
    )

    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "git_filter_repo",
            "--force",
            "--commit-callback",
            callback,
        ],
        cwd=REPO,
    )

    DATE_MAP.unlink(missing_ok=True)
    refs_original = REPO / ".git" / "refs" / "original"
    if refs_original.exists():
        shutil.rmtree(refs_original)

    subprocess.check_call(["git", "reflog", "expire", "--expire=now", "--all"], cwd=REPO)
    subprocess.check_call(["git", "gc", "--prune=now"], cwd=REPO)

    first = run("log", "--reverse", "--format=%ai", "-1")
    last = run("log", "--format=%ai", "-1")
    print(f"Rewrote {n} commits")
    print(f"Oldest: {first}")
    print(f"Newest: {last}")


if __name__ == "__main__":
    main()
