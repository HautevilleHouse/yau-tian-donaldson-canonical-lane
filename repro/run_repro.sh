#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${ROOT_DIR}"

python3 scripts/extract_constants.py --inputs artifacts/constants_extraction_inputs.json --out artifacts/constants_extracted.json
python3 scripts/promote_constants.py --extracted artifacts/constants_extracted.json --registry artifacts/constants_registry.json --stitch artifacts/stitch_constants.json --report artifacts/promotion_report.json
python3 scripts/ytd_closure_guard.py --strict-coh-zero --registry artifacts/constants_registry.json --stitch artifacts/stitch_constants.json --out repro/certificate_runtime.json --history repro/drift_guard_runs.jsonl --pretty
python3 scripts/update_manifest.py --manifest repro/repro_manifest.json
python3 scripts/release_gate.py --mode fully_extracted --manifest repro/repro_manifest.json --registry artifacts/constants_registry.json --inputs artifacts/constants_extraction_inputs.json --pretty
echo
echo "wrote ${ROOT_DIR}/repro/certificate_runtime.json"
