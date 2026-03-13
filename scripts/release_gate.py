#!/usr/bin/env python3
"""Release gate checker for normalized vs fully-extracted modes."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

DEFAULT_MANIFEST = "repro/repro_manifest.json"
DEFAULT_REGISTRY = "artifacts/constants_registry.json"
DEFAULT_INPUTS = "artifacts/constants_extraction_inputs.json"
MODES = {"normalized", "fully_extracted"}
ALLOWED_STATUS = {"derived_numeric", "normalized_placeholder"}


def _resolve(path_str: str) -> Path:
    p = Path(path_str).expanduser()
    if p.is_absolute():
        return p
    return PROJECT_ROOT / p


def _finite(v: Any) -> bool:
    return isinstance(v, (int, float)) and math.isfinite(float(v))


def _check_manifest(manifest_path: Path) -> dict[str, Any]:
    data = json.loads(manifest_path.read_text())
    mismatches = []
    missing = []
    for ent in data.get("files", []):
        rel = ent["path"]
        p = PROJECT_ROOT / rel
        if not p.exists():
            missing.append(rel)
            continue
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        if h != ent["sha256"]:
            mismatches.append(rel)
    return {"missing": missing, "mismatches": mismatches, "ok": not missing and not mismatches}


def _check_statuses(inputs_path: Path, mode: str) -> dict[str, Any]:
    data = json.loads(inputs_path.read_text())
    allowed = {"derived_numeric", "normalized_placeholder"}
    bad = []
    non_derived = []
    for group in ("constants", "stitch"):
        obj = data.get(group, {})
        for name, spec in obj.items():
            status = spec.get("status")
            if status not in allowed:
                bad.append(f"{group}.{name}: invalid status {status}")
                continue
            if mode == "fully_extracted" and status != "derived_numeric":
                non_derived.append(f"{group}.{name}")
    return {
        "invalid": bad,
        "non_derived": non_derived,
        "ok": not bad and (mode != "fully_extracted" or not non_derived),
    }


def _check_registry(registry_path: Path) -> dict[str, Any]:
    data = json.loads(registry_path.read_text())
    bad = []
    for name, ent in data.get("constants", {}).items():
        if not isinstance(ent, dict):
            bad.append(f"{name}: not object")
            continue
        if not ent.get("theorem_level", False):
            bad.append(f"{name}: theorem_level false")
        if not _finite(ent.get("value")):
            bad.append(f"{name}: non-finite value")
        if ent.get("status") not in ALLOWED_STATUS:
            bad.append(f"{name}: invalid status")
        if not str(ent.get("source", "")).strip():
            bad.append(f"{name}: missing source")
        if not str(ent.get("source_section", "")).strip():
            bad.append(f"{name}: missing source_section")
        if not str(ent.get("notes", "")).strip():
            bad.append(f"{name}: missing notes")
    return {"issues": bad, "ok": not bad}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", default="normalized", choices=sorted(MODES))
    ap.add_argument("--manifest", default=DEFAULT_MANIFEST)
    ap.add_argument("--registry", default=DEFAULT_REGISTRY)
    ap.add_argument("--inputs", default=DEFAULT_INPUTS)
    ap.add_argument("--pretty", action="store_true")
    ns = ap.parse_args()

    manifest_path = _resolve(ns.manifest)
    registry_path = _resolve(ns.registry)
    inputs_path = _resolve(ns.inputs)

    manifest = _check_manifest(manifest_path)
    statuses = _check_statuses(inputs_path, ns.mode)
    registry = _check_registry(registry_path)

    report = {
        "schema_version": "2026-03-05",
        "generated_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "mode": ns.mode,
        "manifest": manifest,
        "statuses": statuses,
        "registry": registry,
    }
    report["ok"] = manifest["ok"] and statuses["ok"] and registry["ok"]

    if ns.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(json.dumps(report, sort_keys=True))

    if not report["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
