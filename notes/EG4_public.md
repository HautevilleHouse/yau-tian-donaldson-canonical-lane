# EG4 Public Note (Rigidity and Endpoint Transfer)

Mature wording: `bad-limit exclusion / endpoint transfer`.

In-paper anchor: `paper/YAU_TIAN_DONALDSON_PREPRINT.md` (`YTD_G4`, `YTD_G5`).

## Goal
Separate the rigidity job from the endpoint-transfer job for `proving equivalence of K-stability and Kähler-Einstein endpoint persistence in the declared admissible class through an admissible Kähler-Einstein closure architecture`.
The older wording `rigidity and endpoint-transfer` corresponds to bad-limit exclusion plus the bridge into the intended endpoint object.

## Objects

- bad-limit class: candidates extracted by the compactness gate but incompatible with closure.
- rigidity floor: `rho_rigidity`.
- endpoint-transfer lock: `k-stability_transfer`.
- coherence interface: `eps_coh` remains available to the bridge and final margin.

## Closure Criterion

`YTD_G4` closes when `rho_rigidity` excludes bad endpoint alternatives: bad nef-divisor countermetrics are excluded.
`YTD_G5` closes when `k-stability_transfer` transfers the surviving endpoint to the intended target class: rigid limit transfers to the k-stability endpoint class.
Together they feed the strict margin `M_YTD`.

## Lemma Chain and Proof Payload

### Lemma EG4.1 (bad-limit exclusion)
Every extracted bad limit contradicts a declared rigidity constraint or leaves the admissible class.

Payload: verify `rho_rigidity` in the registry and certificate surfaces.

### Lemma EG4.2 (endpoint transfer)
The surviving rigid representative is locked to the standard problem-side endpoint by `k-stability_transfer`.

Payload: read this note together with `notes/IDENTIFICATION_BRIDGE.md`.

### Theorem EG4.3 (rigidity/transfer gate closure)
If bad limits are excluded and the endpoint lock is active, then `YTD_G4` and `YTD_G5` deliver the boundary object needed by the final margin.

## Current Instantiation

- rigidity gate: `YTD_G4`
- rigidity artifact key: `rho_rigidity`
- transfer gate: `YTD_G5`
- transfer artifact key: `k-stability_transfer`
- mature equivalent: `bad-limit exclusion / endpoint identification`
- audit surface: `notes/IDENTIFICATION_BRIDGE.md` and `repro/certificate_runtime.json`
