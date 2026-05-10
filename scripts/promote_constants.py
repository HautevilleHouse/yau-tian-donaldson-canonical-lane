#!/usr/bin/env python3
"""Promote extracted constants into registry/stitch files with theorem-level tags."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

DEFAULT_EXTRACTED = "artifacts/constants_extracted.json"
DEFAULT_REGISTRY = "artifacts/constants_registry.json"
DEFAULT_STITCH = "artifacts/stitch_constants.json"
DEFAULT_REPORT = "artifacts/promotion_report.json"


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


def _finite(v: Any) -> bool:
    return isinstance(v, (int, float)) and math.isfinite(float(v))


def _assert_ok(name: str, entry: dict[str, Any]) -> None:
    checks = entry.get("validations", {})
    if not checks.get("ok", False):
        raise ValueError(f"extracted validation failed for {name}: {checks}")
    value = entry.get("normalized_value")
    if not _finite(value):
        raise ValueError(f"normalized value is not finite for {name}: {value}")
    status = entry.get("status")
    if status not in {"derived_numeric", "normalized_placeholder"}:
        raise ValueError(f"invalid extracted status for {name}: {status}")
    source_section = str(entry.get("source_section", "")).strip()
    if not source_section:
        raise ValueError(f"missing source_section for {name}")


def promote(
    extracted: dict[str, Any],
    registry_path: Path,
    stitch_path: Path,
) -> dict[str, Any]:
    reg = {"constants": {}}
    if registry_path.exists():
        reg = json.loads(registry_path.read_text())
    reg_consts = reg.setdefault("constants", {})

    promoted: dict[str, Any] = {}
    for key, ent in extracted.get("constants", {}).items():
        _assert_ok(key, ent)
        promoted_value = float(ent["normalized_value"])
        reg_consts[key] = {
            "value": promoted_value,
            "theorem_level": True,
            "status": ent["status"],
            "source": f"artifacts/constants_extracted.json#{key}",
            "source_section": ent["source_section"],
            "notes": (
                "Promoted by extraction pipeline; "
                f"status={ent['status']}; "
                f"source_section={ent['source_section']}; "
                f"raw={ent['raw_value']}, ref={ent['reference']}, formula={ent['formula']}"
            ),
        }
        promoted[key] = promoted_value

    stitch = {"constants": {}}
    if stitch_path.exists():
        stitch = json.loads(stitch_path.read_text())
    stitch_consts = stitch.setdefault("constants", {})
    promoted_stitch: dict[str, Any] = {}
    for key, ent in extracted.get("stitch", {}).items():
        _assert_ok(key, ent)
        promoted_value = float(ent["normalized_value"])
        stitch_consts[key] = {
            "value": promoted_value,
            "theorem_level": True,
            "status": ent["status"],
            "source": f"artifacts/constants_extracted.json#stitch.{key}",
            "source_section": ent["source_section"],
            "notes": (
                "Promoted by extraction pipeline; "
                f"status={ent['status']}; "
                f"source_section={ent['source_section']}; "
                f"raw={ent['raw_value']}, ref={ent['reference']}, formula={ent['formula']}"
            ),
        }
        promoted_stitch[key] = promoted_value

    registry_path.parent.mkdir(parents=True, exist_ok=True)
    stitch_path.parent.mkdir(parents=True, exist_ok=True)
    reg["updated_at_utc"] = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    _write_json_stable(registry_path, reg, volatile_keys=("updated_at_utc",))
    _write_json_stable(stitch_path, stitch, volatile_keys=())

    return {"promoted_constants": promoted, "promoted_stitch": promoted_stitch}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--extracted", default=DEFAULT_EXTRACTED)
    ap.add_argument("--registry", default=DEFAULT_REGISTRY)
    ap.add_argument("--stitch", default=DEFAULT_STITCH)
    ap.add_argument("--report", default=DEFAULT_REPORT)
    ap.add_argument("--pretty", action="store_true")
    ns = ap.parse_args()

    extracted_path = _resolve(ns.extracted)
    registry_path = _resolve(ns.registry)
    stitch_path = _resolve(ns.stitch)
    report_path = _resolve(ns.report)

    extracted = json.loads(extracted_path.read_text())
    result = promote(extracted, registry_path=registry_path, stitch_path=stitch_path)
    report = {
        "schema_version": "2026-03-05",
        "generated_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "framework": extracted.get("framework", ""),
        "extracted_source": str(extracted_path.relative_to(PROJECT_ROOT)),
        "registry_path": str(registry_path.relative_to(PROJECT_ROOT)),
        "stitch_path": str(stitch_path.relative_to(PROJECT_ROOT)),
        **result,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_json_stable(report_path, report, volatile_keys=("generated_utc",))

    if ns.pretty:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
