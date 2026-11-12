# ErrataLink

ErrataLink checks whether one version-pinned correction affects a cited section or table cell. A correction elsewhere in a document should not invalidate a citation automatically. An ambiguous locator or changed notice should not be treated as a clear bill of health.

- [Public dashboard](https://erratalink.tinymule33.chatgpt.site/)
- [Studionet contract](https://explorer-studio.genlayer.com/address/0xBF78Ac0f1cb4BF5E6e594c01830567734242A37F)
- [Live verification and reproduction](docs/LIVE_VERIFICATION.md)
- [Project Explorer submission details](docs/PROJECT_EXPLORER.md)

## How consensus works

`verify(document, locator, notice, pin)` validates bounded IDs and derives the evidence URLs from a fixed source policy. The leader and validators independently retrieve the original document and correction and compute the result under GenLayer's strict Equivalence Principle. They agree on the input identity, affected location, change type, verdict, reason, evidence references, and original document digest. The contract records the agreed result and its SHA-256. The review ID is the SHA-256 of the compact UTF-8 JSON array of method arguments, so repeated requests with the same evidence pin reuse the result.

`get_review(review_id)` reads the stored decision. An empty string indicates the review does not exist in the queried state. `policy()` returns the deployed ruleset identifier.

| Mode | Accepted input | Evidence |
|---|---|---|
| RFC section | RFC number such as `rfc9110`, section such as `B.1`, verified erratum ID | RFC Editor's immutable RFC text and the verified notice block in its informative inline errata rendering |
| Table demonstration | `harbor-v1`, a locator such as `table:2/east.weekday`, notice `1` | Fictional table and one-cell correction, both pinned by commit and SHA-256 |

The RFC notice pin is SHA-256 over the compact, ASCII-escaped JSON array `[section, original_text, corrected_text]` extracted from the verified block. Decode HTML entities, strip markup, and collapse whitespace within each value. Use the printed section label in the pin, including any trailing period. Table pins hash the exact notice bytes.

A same section, enclosing section, or same cell can return `AFFECTED`. A verified disjoint locator can return `UNAFFECTED`. A missing citation, a notice scoped only to an ancestor of the citation, or a mismatched notice pin yields `INCONCLUSIVE`. This release classifies explicit replacements. Multi-location and global notices, publisher formats beyond the documented RFC layout, and arbitrary research-document uploads are outside its supported scope. A successful verdict covers one notice and locator.

The contract accepts no arbitrary fetch URL and sends no evidence to a language model. Evidence that cannot be retrieved or exceeds the size limit fails execution and can be retried. Missing or unsupported notice blocks that return readable content are recorded conservatively as inconclusive for the given request. A new notice revision uses a new pin and review ID. Original RFC byte fingerprints are compared across validators and recorded for review.

## Develop locally

```sh
npm ci
python -m unittest discover -s tests -v
npm test
npm run build
python -m http.server 8000 --directory dist
```

The frontend prepares the Studio inputs, reads finalized state through GenLayerJS, and tracks consensus and execution separately. Deployments and writes use Studio's built-in test account. The public app requires no account to read or track a review.

- [GenLayer Studio documentation](https://docs.genlayer.com/developers/intelligent-contracts/tools/genlayer-studio)
- [Equivalence Principle](https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle)
- [RFC Editor errata process](https://www.rfc-editor.org/series/rfc-errata/)
