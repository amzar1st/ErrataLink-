# Live verification

ErrataLink was deployed on **Studionet, chain 61999** in Normal (Full Consensus) mode. GenLayer Studio's built-in account `0x56944456AEFf47F7312a4D8c8b712558E86D68Bf` signed the deployment and all five writes.

- [Public dashboard](https://erratalink.tinymule33.chatgpt.site/)
- [Deployed contract and published source](https://explorer-studio.genlayer.com/address/0xBF78Ac0f1cb4BF5E6e594c01830567734242A37F)
- [Repository source](../contracts/errata_link.py). Git blob `869ea9657e910f9bc4b98de0a893d35181c0f1a8`.
- SHA-256 of the explorer's displayed source and repository file `acf59f52e4cf028d837f161092464e8c6d3d662801f80e941ea5b81dec2a2032`.

| Case | Finalized receipt | Observed outcome |
| --- | --- | --- |
| Deploy | [Receipt](https://explorer-studio.genlayer.com/tx/0xe1c5a43b474c0028328e9bf5f56719ff021ce4c7bdd0dca470ceaf2f3028ea20) | Execution succeeded |
| Harbor table 2, east weekday | [Receipt](https://explorer-studio.genlayer.com/tx/0x36d351bc2eed6d0cc2b42042067828c73f660c0534030322ebc7cccf8d8b4c5e) | `AFFECTED` |
| Harbor table 2, west weekday | [Receipt](https://explorer-studio.genlayer.com/tx/0xceb78b8500410611879fc6277f49af18bbb0936f82cd9ed4c29befc51eb19ba9) | `UNAFFECTED` |
| RFC 9110 §B.1, EID 7105 | [Receipt](https://explorer-studio.genlayer.com/tx/0xd8573b14b2a73125908773ea89172ac136503cba833caf92d65f03d8fe2142a5) | `AFFECTED` |
| Harbor table 2, incorrect notice digest | [Receipt](https://explorer-studio.genlayer.com/tx/0x16f2367ba73480d68eb6acda122c7a7e1a218302af9fa8dfa4e2418249aa6a59) | `INCONCLUSIVE`, evidence hash mismatch |
| Invalid locator | [Receipt](https://explorer-studio.genlayer.com/tx/0x2235c23035787e975872ef20b213e40d9c870569d5ba3f8c2c379cbbc43f23b4) | GenVM execution error |

| Case | Review ID | Decision SHA-256 |
| --- | --- | --- |
| Corrected cell | `99faf30e1889e5719adfbde0c014c80b3984cfc1a2b76402b5b1f2148b4776f0` | `c733ab8e872aaff4cb3457e78b46cba25b275575ac269fe2cd460bd090a186c1` |
| Neighboring cell | `d0f4b8afb291b27f29ec23d68189570ae76e5236591850b42477d675858e1702` | `97809cf634208dd8fcc89489c1e8929c16cb974d7262d4c08dc907f26ba22adf` |
| RFC 9110 | `f3c14708084609c032968a4d3c686bab1ab47b90e44379f5da89f8f2b3eaa329` | `2b66265f1470cc4d2b195a6825cc1ba460d8edc842fe60790863ca8013bb52ae` |
| Incorrect notice digest | `c4d5d43760a7add14a4252752e216a2fff4a973920f07926f0af8b087e5284e9` | `53343042faf5bf9c914c72f134dbb761982c968f2ff968036c0827761b5fa9e9` |

## Reproduce

1. On the public dashboard select **Corrected cell**, **Other cell**, or **RFC 9110** to load the sample inputs, compute the review ID, read the corresponding finalized result, and track its original transaction.
2. To reproduce a write, open GenLayer Studio. In **Contracts**, use the import-by-address control and select the deployed address shown above. Open **Run and Debug**, leave **Normal (Full Consensus)** selected, and open `verify`.
3. Select **Prepare Studio transaction** in the dashboard to see the four arguments. Enter them in Studio under the respective parameter names and submit using a built-in test account. Duplicate inputs reuse the existing review.
4. Paste the resulting transaction hash into **Track a transaction**. The dashboard distinguishes consensus finalization from execution success, then reads the finalized review by its ID.
5. For an independent lookup, choose **Contract → Read Contract → get_review** in the explorer and query any review ID above.

Nine Python regression tests, three JavaScript tests, the frontend build, and Studio GenVM schema validation passed. Live execution tested the two table locators, the authoritative RFC notice, a digest mismatch, and invalid input. Signing is performed in Studio and the dashboard provides read and receipt tracking.
