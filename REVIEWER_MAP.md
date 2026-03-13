# Reviewer Map

## Claim Scope

- Canonical-lane claim: inside the `manifold_constrained` lane, if the theorem chain in this repository holds and the guard certificate passes, the repository-level closure claim is satisfied.
- Standard target claim: carried by the in-repo bridge theorems tying the lane to the target statement.

## Theorem Dependency Chain

1. `EG1`: coercive response and active control floor.
2. `EG2`: capture and admissible continuation.
3. `EG3`: compactness and no-collapse spacing.
4. `EG4`: rigidity and transfer.
5. Identification bridge: strict coherence on the determining class.
6. Scalar closure: `YTD_G1`, `YTD_G2`, `YTD_G3`, `YTD_G4`, `YTD_G5`, `YTD_G6`, `YTD_GM` all `PASS`.

Primary files:

- `paper/YAU_TIAN_DONALDSON_PREPRINT.md`
- `notes/EG1_public.md`
- `notes/EG2_public.md`
- `notes/EG3_public.md`
- `notes/EG4_public.md`
- `notes/IDENTIFICATION_BRIDGE.md`

## Closure Gates

| Gate | Constant | Description |
|------|----------|-------------|
| `YTD_G1` | `kappa_canonical` | projected Kähler-Einstein response has a strict positive floor |
| `YTD_G2` | `sigma_degeneration` | metric-degeneration defect stays above capture floor across admissible metric losses |
| `YTD_G3` | `kappa_compact` | normalized near-failure families are precompact and admissible windows do not collapse |
| `YTD_G4` | `rho_rigidity` | bad nef-divisor countermetrics are excluded |
| `YTD_G5` | `k-stability_transfer` | rigid limit transfers to the k-stability endpoint class |
| `YTD_G6` | `eps_coh` | strict coherence / identification closure |
| `YTD_GM` | derived | final strict margin |

## Falsification Conditions

- `repro/certificate_runtime.json` has any non-`PASS` gate.
- `lane.active_lane != "manifold_constrained"`.
- `all_pass != true`.
- Any manifest hash mismatch under `repro/repro_manifest.json`.
- A verified counterexample to any EG theorem statement used in the paper.
