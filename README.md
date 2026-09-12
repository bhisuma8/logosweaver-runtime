# LogosWeaver Runtime

## Experimental runtime implementation for the LogosWeaver Pre-LLM Natural Language Compiler.

LogosWeaver Runtime

Current lineage: v0.5  
Current implementation: v0.5.4  
Status: Behavioral Freeze

This repository contains the experimental runtime implementation of the LogosWeaver Pre-LLM Natural Language Compiler.

The current v0.5 implementation establishes:

- Runtime judgment
    
- Response Gate
    
- Response Permission
    
- Response Output Boundary
    
- Dialogue Response
    
- Response Emission
    

v0.5 is behaviorally frozen as of Phase E.1.

## Lineage

v0.1 → v0.2 → v0.3 → v0.4 → v0.5

## Documentation Lineage

Phase E documentation records are maintained under:

`docs/lineage/`

The Phase E records document evaluation, boundary, continuity, preservation, and closure decisions around the frozen v0.5.4 Runtime.

These records do not constitute new Runtime version releases.

## Injection Snapshot

The canonical cross-session injection baseline is maintained under:

`docs/snapshots/LW_Runtime_v0.5.4_INJECTION_SNAPSHOT.md`

The snapshot preserves the v0.5.4 Runtime baseline, incorporates the E.5-approved `SemanticCondition` representation refinement, and includes the E.2/E.3 evaluation tests subsequently synchronized to the repository.

The pre-refinement FULL SOURCE is not duplicated as a separate repository artifact.

## Public Repository Boundary

This repository is publicly observable, but public exposure, repository activity, or Git operations such as forking and branching do not by themselves constitute LogosWeaver Semantic Lineage or Lineage Membership.

The v0.5.4 Runtime does not include a production external ingress, API, or UI.

This repository is therefore not presented as a public runtime service or end-user application.

## License

This repository is proprietary and is not released under an open-source license.

Copyright (c) 2026 Chang Dai Park. All rights reserved.

See `LICENSE` for the applicable terms.
