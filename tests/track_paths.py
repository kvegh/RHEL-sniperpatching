"""Choose the independent playbook tree exercised by the existing test suite."""
import os
from pathlib import Path

TRACK = os.environ.get("SNIPER_TRACK", "old")
if TRACK not in {"old", "new"}:
    raise ValueError("SNIPER_TRACK must be old or new")
TRACK_ROOT = Path(__file__).resolve().parents[1] / "playbooks" / TRACK
