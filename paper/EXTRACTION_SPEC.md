# Extraction Specification

This repository uses the standard canonical-lane extraction pipeline.

Required constants:

- `kappa_canonical` from `c_canonical_raw * canonical_density_raw - e_canonical_raw`
- `sigma_degeneration` from `degeneration_floor_raw - metric_loss_raw - restart_loss_raw`
- `kappa_compact` from `1.0 / (1.0 + delta_comp_sup_raw)`
- `rho_rigidity` from `rho_rigidity_raw`
- `k-stability_transfer` from `c_transfer_raw * transfer_gain_raw - e_transfer_raw`
- `eps_coh` from `eps_coh_raw`
- stitch constant `sigma_star_can` from `sigma_star_can_raw`

Pipeline order:

1. `scripts/extract_constants.py`
2. `scripts/promote_constants.py`
3. `scripts/ytd_closure_guard.py`
4. `scripts/update_manifest.py`
5. `scripts/release_gate.py --mode fully_extracted`
