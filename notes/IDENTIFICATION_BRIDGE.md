# Identification Bridge

Mature wording: `endpoint identification / boundary object / final margin`.

In-paper anchor: `paper/YAU_TIAN_DONALDSON_PREPRINT.md` (bridge and margin interface).

## Goal
Identify the canonical endpoint representative with the ordinary problem-side target for `proving equivalence of K-stability and Kähler-Einstein endpoint persistence in the declared admissible class through an admissible Kähler-Einstein closure architecture`.
This is the boundary/global-object step in the public Canonical Lane package.

## Objects

- canonical endpoint representative: the surviving endpoint object produced by the gate chain.
- problem-side target: the ordinary mathematical target statement named in the main preprint.
- endpoint lock: `k-stability_transfer`.
- coherence remainder: `eps_coh`.

## Determining Class

The determining class is the collection of observables, locks, or transfer constraints declared by the main preprint and constants registry. In the older wording this appears as an endpoint lock; in the mature wording it is endpoint identification.

## Closure Criterion

The bridge closes when:

1. the projected/core, transport, compactness, and rigidity gates have supplied their inputs;
2. the endpoint-transfer lock `k-stability_transfer` identifies the surviving representative;
3. the coherence remainder `eps_coh` is not smuggled into the endpoint;
4. the strict closure margin `M_YTD` remains positive.

## Lemma Chain and Proof Payload

### Lemma ID.1 (lock persistence)
Endpoint locks persist along the admissible extracted lane when the transport and compactness gates have closed.

Payload: verify `k-stability_transfer` against the constants registry and runtime certificate.

### Lemma ID.2 (determining-class uniqueness)
Two admissible endpoint representatives that agree on the declared determining locks are equivalent under the repo's declared endpoint equivalence.

Payload: compare the main preprint's target statement with the bridge language in this file.

### Theorem ID.3 (coherence/identification closure)
If lock persistence, determining-class uniqueness, and strict coherence hold, then the endpoint representative is identified and the final margin `M_YTD` is meaningful.

## Current Instantiation

- endpoint-transfer artifact key: `k-stability_transfer`
- coherence artifact key: `eps_coh`
- margin: `M_YTD`
- mature equivalent: `endpoint identification / boundary object / final margin`
- audit surface: `repro/run_repro.sh`, `repro/certificate_runtime.json`, and `artifacts/constants_registry.json`
