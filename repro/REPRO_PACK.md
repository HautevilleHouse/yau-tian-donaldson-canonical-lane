# Repro Pack

`bash repro/run_repro.sh` deterministically:

1. extracts theorem constants from `artifacts/constants_extraction_inputs.json`,
2. promotes them into the registry and stitch artifacts,
3. runs `scripts/ytd_closure_guard.py` in strict coherence mode,
4. refreshes `repro/repro_manifest.json`,
5. enforces `fully_extracted` release-gate mode.

## Pass condition

- `repro/certificate_runtime.json` has `all_pass == true`,
- all native gates are `PASS`,
- strict margin `M_YTD = 0.8051529790660226`,
- `repro/repro_manifest.json` has no missing files or hash mismatches.
