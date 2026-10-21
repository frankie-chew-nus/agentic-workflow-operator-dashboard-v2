# W6 B→C integration decision — batch work

**State: EXPERIMENTAL ONLY / ACTIVE HOLD**

## Parallel workstreams

1. **Authority binding:** `b_release_authority_binding_v1.py` supports disposable positive and negative cases only. The positive test uses an injected mock verifier, **not** an authenticated Human decision. Live activation is always denied.
2. **Release-history reconciliation:** The observed `RES-XAUUSD` dashboard decision `DEC-F34D70261D` for `CAND-B-002` is linked to a frozen C boundary by B release artifact hash, but Human identity and historical completeness are not verified.
3. **Resource/dependency closure:** T04 ATR and previous-day OHLC contracts and T05 live dependency inventory remain unverified. Approval of policy definitions does not establish available resources.
4. **Disposable HTTP gate:** Existing HTTP negative test passed; no live-positive HTTP test or active deployment has occurred.

## Exit criteria

- Independently authenticated Operator decisions and complete commission release ledger.
- Verified T04 resource inventory and T05 dependency inventory.
- Real fail-closed active-path design reviewed separately and approved by Human.
- Disposable HTTP negative and positive paths, existing regression and rollback checks.
- Separate active deployment approval. No merge to main until then.

**Do not substitute a mock verifier or synthetic test fixture for real authority.**
