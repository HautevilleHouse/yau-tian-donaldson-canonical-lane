#!/usr/bin/env python3
"""Update SHA256 entries in repro manifest from current repository files."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

DEFAULT_MANIFEST = "repro/repro_manifest.json"


def _resolve(path_str: str) -> Path:
    p = Path(path_str).expanduser()
    if p.is_absolute():
        return p
    return PROJECT_ROOT / p


def _write_json_stable(path: Path, data: dict[str, Any], volatile_keys: tuple[str, ...]) -> None:
    existing = None
    if path.exists():
        try:
            existing = json.loads(path.read_text())
        except Exception:
            existing = None
    if isinstance(existing, dict):
        current = dict(data)
        prior = dict(existing)
        for key in volatile_keys:
            current.pop(key, None)
            prior.pop(key, None)
        if current == prior:
            for key in volatile_keys:
                if key in existing:
                    data[key] = existing[key]
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", default=DEFAULT_MANIFEST)
    ap.add_argument("--pretty", action="store_true")
    ns = ap.parse_args()

    manifest_path = _resolve(ns.manifest)
    data = json.loads(manifest_path.read_text())
    files = data.get("files", [])
    if not isinstance(files, list):
        raise ValueError("manifest files must be list")

    for ent in files:
        rel = ent["path"]
        p = PROJECT_ROOT / rel
        if not p.exists():
            raise FileNotFoundError(f"manifest path missing: {rel}")
        ent["sha256"] = hashlib.sha256(p.read_bytes()).hexdigest()

    data["generated_utc"] = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    _write_json_stable(manifest_path, data, volatile_keys=("generated_utc",))

    out = {"manifest": str(manifest_path.relative_to(PROJECT_ROOT)), "files": len(files)}
    if ns.pretty:
        print(json.dumps(out, indent=2, sort_keys=True))
    else:
        print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()

