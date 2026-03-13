#!/usr/bin/env python3
"""Canonical-lane closure guard for the Yau-Tian-Donaldson conjecture workspace."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

DEFAULT_REGISTRY = 'artifacts/constants_registry.json'
DEFAULT_STITCH = 'artifacts/stitch_constants.json'
DEFAULT_OUT = 'repro/certificate_runtime.json'
DEFAULT_HISTORY = 'repro/drift_guard_runs.jsonl'

PRIMARY_KEYS = (
    'kappa_canonical',
    'sigma_degeneration',
    'kappa_compact',
    'rho_rigidity',
    'k-stability_transfer',
)
COHERENCE_KEY = 'eps_coh'


def _finite(v: Any) -> bool:
    return isinstance(v, (int, float)) and math.isfinite(float(v))


def _resolve(path_str: str) -> Path:
    p = Path(path_str).expanduser()
    return p if p.is_absolute() else PROJECT_ROOT / p


def _bootstrap_registry(path: Path) -> None:
    payload = {'constants': {key: {'value': None, 'theorem_level': False, 'source': '', 'notes': 'pending theorem extraction'} for key in (*PRIMARY_KEYS, COHERENCE_KEY)}}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _load_registry(path: Path) -> dict[str, Any]:
    if not path.exists():
        _bootstrap_registry(path)
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError('registry must be JSON object')
    consts = data.get('constants')
    if not isinstance(consts, dict):
        raise ValueError('registry missing constants object')
    return data


def _load_sigma_from_stitch(path: Path) -> float | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
    except Exception:
        return None
    consts = data.get('constants')
    if not isinstance(consts, dict):
        return None
    sigma = consts.get('sigma_star_can')
    if isinstance(sigma, dict):
        v = sigma.get('value')
        return float(v) if _finite(v) else None
    return float(sigma) if _finite(sigma) else None


def _entry(constants: dict[str, Any], key: str) -> tuple[float | None, bool]:
    obj = constants.get(key)
    if isinstance(obj, dict):
        v = obj.get('value')
        theorem = bool(obj.get('theorem_level', False))
        return (float(v) if _finite(v) else None, theorem)
    if _finite(obj):
        return float(obj), False
    return None, False


def compute_report(data: dict[str, Any], sigma_star: float | None, strict_coh_zero: bool) -> dict[str, Any]:
    consts = data['constants']
    primary_values = {}
    primary_theorem = {}
    for key in PRIMARY_KEYS:
        value, theorem = _entry(consts, key)
        primary_values[key] = value
        primary_theorem[key] = theorem
    eps_coh, theorem_coh = _entry(consts, COHERENCE_KEY)
    gate_pass = [primary_theorem[k] and _finite(primary_values[k]) and float(primary_values[k]) > 0.0 for k in PRIMARY_KEYS]
    coh_base = theorem_coh and _finite(eps_coh) and float(eps_coh) >= 0.0
    coh_pass = coh_base and ((abs(float(eps_coh)) < 1e-15) if strict_coh_zero else True)
    margin = None
    if all(_finite(primary_values[k]) for k in PRIMARY_KEYS) and _finite(eps_coh):
        margin = min(float(primary_values[k]) for k in PRIMARY_KEYS) - float(eps_coh)
    gm_pass = all(gate_pass) and coh_pass and _finite(margin) and float(margin) > 0.0
    native_names = ['YTD_G1', 'YTD_G2', 'YTD_G3', 'YTD_G4', 'YTD_G5']
    gates = {name: ('PASS' if passed else 'FAIL') for name, passed in zip(native_names, gate_pass)}
    gates['YTD_G6'] = 'PASS' if coh_pass else 'FAIL'
    gates['YTD_GM'] = 'PASS' if gm_pass else 'FAIL'
    blockers = {}
    for name, key, passed in zip(native_names, PRIMARY_KEYS, gate_pass):
        blockers[name] = [] if passed else [f'{key} missing/nonpositive or not theorem-level']
    blockers['YTD_G6'] = [] if coh_pass else ['eps_coh missing/invalid or strict-zero target failed']
    blockers['YTD_GM'] = [] if gm_pass else ['strict margin <= 0 or upstream gates failed']
    normalized_gates = {'G1': gates['YTD_G1'], 'G2': gates['YTD_G2'], 'G3': gates['YTD_G3'], 'G4': gates['YTD_G4'], 'G5': gates['YTD_G5'], 'G6': 'NA', 'GCoh': gates['YTD_G6'], 'GM': gates['YTD_GM']}
    normalized_blockers = {'G1': blockers['YTD_G1'], 'G2': blockers['YTD_G2'], 'G3': blockers['YTD_G3'], 'G4': blockers['YTD_G4'], 'G5': blockers['YTD_G5'], 'G6': [], 'GCoh': blockers['YTD_G6'], 'GM': blockers['YTD_GM']}
    report = {'meta': {'computed_at_utc': dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(), 'framework': 'yau_tian_donaldson'}, 'schema': {'normalized_gate_keys': ['G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'GCoh', 'GM'], 'g6_policy': 'NA means this framework has no standalone pre-coherence G6 gate'}, 'lane': {'canonical_theorem_lane': 'manifold_constrained', 'active_lane': 'manifold_constrained'}, 'inputs': {**primary_values, 'eps_coh': eps_coh, 'sigma_star_can': sigma_star}, 'derived': {'strict_margin': margin, 'strict_coh_zero': bool(strict_coh_zero)}, 'gates': gates, 'blockers': blockers, 'normalized': {'gates': normalized_gates, 'blockers': normalized_blockers}}
    report['all_pass'] = all(v == 'PASS' for v in gates.values())
    report['all_pass_normalized'] = all(v in {'PASS', 'NA'} for v in normalized_gates.values()) and all(v == 'PASS' for v in normalized_gates.values() if v != 'NA')
    return report


def append_history(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {'timestamp_utc': report['meta']['computed_at_utc'], 'all_pass': report['all_pass'], 'gates': report['gates'], 'strict_margin': report['derived']['strict_margin']}
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--registry', default=DEFAULT_REGISTRY)
    ap.add_argument('--stitch', default=DEFAULT_STITCH)
    ap.add_argument('--out', default=DEFAULT_OUT)
    ap.add_argument('--history', default=DEFAULT_HISTORY)
    ap.add_argument('--strict-coh-zero', action='store_true')
    ap.add_argument('--pretty', action='store_true')
    ns = ap.parse_args()
    registry_path = _resolve(ns.registry)
    stitch_path = _resolve(ns.stitch)
    out_path = _resolve(ns.out)
    history_path = _resolve(ns.history)
    report = compute_report(_load_registry(registry_path), _load_sigma_from_stitch(stitch_path), bool(ns.strict_coh_zero))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2 if ns.pretty else None, sort_keys=True) + "\n")
    append_history(history_path, report)
    print(json.dumps(report, indent=2 if ns.pretty else None, sort_keys=True))


if __name__ == '__main__':
    main()
