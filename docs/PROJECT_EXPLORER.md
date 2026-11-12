# GenLayer Project Explorer

| Field | Value |
| --- | --- |
| Contribution | Builder → Projects |
| Project name | ErrataLink |
| Suggested tags | Oracles, with Data Verification and Research if available |
| One-liner | Verify whether a version-pinned correction changes the RFC section or table cell you cite, with a finalized GenLayer verdict and linked evidence. |
| Repository | https://github.com/amzar1st/ErrataLink- |
| Public frontend | https://erratalink.tinymule33.chatgpt.site/ |
| Contract | https://explorer-studio.genlayer.com/address/0xBF78Ac0f1cb4BF5E6e594c01830567734242A37F |
| Supporting information | https://github.com/amzar1st/ErrataLink-/blob/main/docs/LIVE_VERIFICATION.md |
| Authoritative data demo | https://explorer-studio.genlayer.com/tx/0xd8573b14b2a73125908773ea89172ac136503cba833caf92d65f03d8fe2142a5 |

## Overview

ErrataLink helps standards implementers and researchers check whether a specific correction affects the material they cited. GenLayer validators independently retrieve the versioned source and correction, then agree on the affected location, change type, evidence references, and verdict. Results are stored as AFFECTED, UNAFFECTED, or INCONCLUSIVE with a reproducible review ID and decision hash. The public dashboard reads finalized state, prepares transactions for GenLayer Studio's built-in account, and tracks consensus and execution. The live demo checks a verified RFC Editor notice for RFC 9110 and shows how a fictional one-cell correction affects one table citation while leaving a neighboring citation unaffected.
