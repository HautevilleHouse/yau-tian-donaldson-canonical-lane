#!/usr/bin/env python3
"""Extract problem-native constants from explicit derivation inputs."""

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

DEFAULT_INPUTS = "artifacts/constants_extraction_inputs.json"
DEFAULT_OUT = "artifacts/constants_extracted.json"
ALLOWED_STATUS = {"derived_numeric", "normalized_placeholder"}
VALIDATION_KEYS = ("required_positive", "required_nonnegative", "strict_zero")

ALLOWED_FUNCS = {
    "min": min,
    "max": max,
    "abs": abs,
}


def _resolve(path_str: str) -> Path:
    p = Path(path_str).expanduser()
    if p.is_absolute():
        return p
    return PROJECT_ROOT / p


def _finite(v: Any) -> bool:
    return isinstance(v, (int, float)) and math.isfinite(float(v))


def _eval_formula(formula: str, components: dict[str, float]) -> float:
    env: dict[str, Any] = {"__builtins__": {}}
    env.update(ALLOWED_FUNCS)
    env.update(components)
    val = eval(formula, env, {})  # noqa: S307 - restricted env and local controlled file
    if not _finite(val):
        raise ValueError(f"formula produced non-finite value: {formula}")
    return float(val)


def _require_fields(name: str, spec: dict[str, Any], required: tuple[str, ...]) -> None:
    missing = [k for k in required if k not in spec]
    if missing:
        raise ValueError(f"missing required fields for {name}: {', '.join(missing)}")


def _require_validation_rule(name: str, spec: dict[str, Any]) -> None:
    if not any(k in spec for k in VALIDATION_KEYS):
        keys = ", ".join(VALIDATION_KEYS)
        raise ValueError(f"missing validation rule for {name}: expected one of {keys}")


def _validate_value(name: str, value: float, spec: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "finite": _finite(value),
        "positive": True,
        "nonnegative": True,
        "strict_zero": True,
    }
    if spec.get("required_positive", False):
        checks["positive"] = value > 0.0
    if spec.get("required_nonnegative", False):
        checks["nonnegative"] = value >= 0.0
    if spec.get("strict_zero", False):
        checks["strict_zero"] = abs(value) < 1e-15
    checks["ok"] = all(v for k, v in checks.items() if k != "ok")
    if not checks["ok"]:
        raise ValueError(f"validation failed for {name}: {checks}")
    return checks


def extract(inputs: dict[str, Any], inputs_sha256: str) -> dict[str, Any]:
    constants: dict[str, Any] = {}
    for name, spec in inputs.get("constants", {}).items():
        if not isinstance(spec, dict):
            raise ValueError(f"constant spec must be object for {name}")
        _require_fields(
            name,
            spec,
            (
                "status",
                "formula",
                "components",
                "reference",
                "source_section",
                "notes",
            ),
        )
        _require_validation_rule(name, spec)
        components = spec.get("components", {})
        if not isinstance(components, dict):
            raise ValueError(f"components must be object for {name}")
        status = str(spec.get("status", "")).strip()
        if status not in ALLOWED_STATUS:
            raise ValueError(f"invalid status for {name}: {status}")
        formula = str(spec.get("formula", "")).strip()
        if not formula:
            raise ValueError(f"missing formula for {name}")
        reference = float(spec.get("reference", 1.0))
        if reference <= 0.0 or not _finite(reference):
            raise ValueError(f"invalid reference for {name}: {reference}")

        raw_value = _eval_formula(formula, {k: float(v) for k, v in components.items()})
        normalized_value = raw_value / reference
        validations = _validate_value(name, normalized_value, spec)

        constants[name] = {
            "status": status,
            "raw_value": raw_value,
            "normalized_value": normalized_value,
            "reference": reference,
            "formula": formula,
            "components": components,
            "required_positive": bool(spec.get("required_positive", False)),
            "required_nonnegative": bool(spec.get("required_nonnegative", False)),
            "strict_zero": bool(spec.get("strict_zero", False)),
            "source_section": spec.get("source_section", ""),
            "notes": spec.get("notes", ""),
            "validations": validations,
        }

    stitch_obj = inputs.get("stitch", {})
    stitch: dict[str, Any] = {}
    for name, spec in stitch_obj.items():
        if not isinstance(spec, dict):
            raise ValueError(f"stitch spec must be object for {name}")
        _require_fields(
            name,
            spec,
            (
                "status",
                "formula",
                "components",
                "reference",
                "source_section",
                "notes",
            ),
        )
        _require_validation_rule(name, spec)
        components = spec.get("components", {})
        if not isinstance(components, dict):
            raise ValueError(f"components must be object for stitch {name}")
        status = str(spec.get("status", "")).strip()
        if status not in ALLOWED_STATUS:
            raise ValueError(f"invalid stitch status for {name}: {status}")
        formula = str(spec.get("formula", "")).strip()
        if not formula:
            raise ValueError(f"missing formula for stitch {name}")
        reference = float(spec.get("reference", 1.0))
        if reference <= 0.0 or not _finite(reference):
            raise ValueError(f"invalid reference for stitch {name}: {reference}")
        raw_value = _eval_formula(formula, {k: float(v) for k, v in components.items()})
        normalized_value = raw_value / reference
        validations = _validate_value(name, normalized_value, spec)
        stitch[name] = {
            "status": status,
            "raw_value": raw_value,
            "normalized_value": normalized_value,
            "reference": reference,
            "formula": formula,
            "components": components,
            "required_positive": bool(spec.get("required_positive", False)),
            "required_nonnegative": bool(spec.get("required_nonnegative", False)),
            "strict_zero": bool(spec.get("strict_zero", False)),
            "source_section": spec.get("source_section", ""),
            "notes": spec.get("notes", ""),
            "validations": validations,
        }

    return {
        "schema_version": "2026-03-05",
        "framework": inputs.get("framework", ""),
        "generated_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "inputs_path": inputs.get("__inputs_path__", ""),
        "inputs_sha256": inputs_sha256,
        "constants": constants,
        "stitch": stitch,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inputs", default=DEFAULT_INPUTS)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--pretty", action="store_true")
    ns = ap.parse_args()

    inputs_path = _resolve(ns.inputs)
    out_path = _resolve(ns.out)

    raw = inputs_path.read_bytes()
    inputs_sha = hashlib.sha256(raw).hexdigest()
    data = json.loads(raw.decode("utf-8"))
    data["__inputs_path__"] = str(inputs_path.relative_to(PROJECT_ROOT))

    extracted = extract(data, inputs_sha)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(extracted, indent=2, sort_keys=True) + "\n")

    if ns.pretty:
        print(json.dumps(extracted, indent=2, sort_keys=True))
    else:
        print(json.dumps({"out": str(out_path), "inputs_sha256": inputs_sha}, sort_keys=True))


if __name__ == "__main__":
    main()
