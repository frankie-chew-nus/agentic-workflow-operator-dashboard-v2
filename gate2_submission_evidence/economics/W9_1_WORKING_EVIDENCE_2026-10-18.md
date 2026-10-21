# W9.1 working evidence — 18 October 2026

Scope: **Week 9 W9.1 working evidence only**, not a complete Gate 2 evidence inventory. Status: evidence index and interpretation only; **not** a replacement for original records or independent verification. Core rule: evidence records what is proved, never upgrades it.

## Architecture and chronology
- A–E governance and CLI workflows preceded the dashboard. Dashboard repository initialized on 2026-10-17 (commit `3647af3`); dashboard is a usability/orchestration enhancement, not the core governance requirement.
- A/B original evidence is in local `Gate2_Evidence/03_WORKSTREAM_A` and `04_WORKSTREAM_B`, with decision collectors in `08_DECISION_RECORDS`. Original artifacts remain local until separately reviewed for safe publication.
- W9.1 eight steps: A research; A→B source approval/release; B formulation; B→C governance; C build/integrity; C Stage 1; D independent OOS; E commissioning. D/E production **not run**, isolated sandbox tests only. CSV M1 OHLC for C versus intended MT5 OOS adapter for D is an architectural separation; adapter implementation/equivalence not independently verified.

## Verified C Stage 1 artifacts (user-supplied)
- Local: `evidence/c_runs/CAND-B-002/v2.1.3/stage1_output/summary.json` and `variant_results.json`.
- Run `S1-AC3049C5FADB`: 54 variants executed, 0 signals in each, 0 performance PASS, 0 explicit FAIL, 54 Human HOLD; `advance_to_d=false` in `c_run_summary.json`.
- Elapsed 2184.235 s (~36.4 min), bounded completed history 72 bars. Full-history equivalence remains unverified; no CPC/drawdown result established.
- Summary references results SHA-256 `169b64a331c74ce127b8dc9836d1e7ded1afe02af7bd77e11ed88222c1b0543e` (source-reported hash; preserve source file).
- Interrupted earlier progress: 8000/354090 (2.3%), elapsed 329.5 s; not a completed equivalence proof.

## C build/rework economics — provisional
- 15 distinct timestamped `atomic_summary.json` records: 2 `HOLD_FOR_HUMAN`, 13 `IMPLEMENTATION_RELEASED`; release does not imply semantic PASS.
- Each of 15 `resource_summary.json` files reports 4 calls, 3585 tokens. A sample ledger shows decomposition 1058, external volatility utility 452, external trailing stop 696, integration 1379, using `gemini-3.1-flash-lite-preview`. No request IDs/timestamps; **do not claim** 15 × 3585 as verified billed consumption.
- 12 distinct semantic `repair_result.json` records report PASS and per-attempt usage. User console output: 24,732 input and 7,344 output = 32,076 total reported tokens. Check deduplication and billing before aggregation.
- API price configuration missing; monetary cost **NOT CALCULATED**.
- Human retrospective estimate given 2026-10-18: approximately 8 h/day project engagement for recent ~7 days, ~4 h/day active (~28 active hours, ~56 total engagement). Covers broad development, CLI work, dashboard, execution and assignment; **not** per-candidate run cost, not measured time tracking.

## A source approval and release — original 2026-10-12 records uploaded
- `20261012T151348531810Z_report.json`: report created, source_count=5, output `operator_review_v1.html`, SHA-256 reported `5b5c5e49b58f83b4393fada61125a7a0af5e16d93125f97ab177467dcc0e089b`.
- `20261012T152241256117Z_approve.json`: approval operation output `research_register_approved_v1.json`, source_count=5, state null; SHA-256 reported `b32bef938a3590406e53f0275669efba01b43ef46d3ac11163cb6e972c9d0cf0`. Do not infer all five approved.
- `20261012T152255553489Z_release.json`: `RELEASE`, source_count=1, output `a_to_b_release_v1.json`, SHA-256 reported `f8339c49428bfd14240a316441d75fb3ccbdae1a13f591da3c6f16c314a8a362`. The exact source identity and Human decision provenance require underlying artifact inspection.
- These JSON events show real A report/approve/release operations, not token/cost accounting or proof of independent source quality.

## D/E and governance
- D sandbox `D_SANDBOX_PASS`, E sandbox `E_COMMISSIONING_BLOCKED_TEST_ARTIFACT`. Sandbox outcomes are not OOS or commissioning authority.
- 117 automated tests passed per Operator report; sanitized Gate 2 archive v4 preserved in branch `feat/evidence-registry-v1`. Four Operator judgement narratives J01–J04 were explicitly approved in chat; approval is not independent artifact verification.
- Strategy logic must not be changed; B-002 must not be advanced past actual C evidence.

## Next evidence steps
1. Inspect actual `research_register_approved_v1.json` and `a_to_b_release_v1.json` before stating exact A admission denominator and reasons.
2. Inspect B formulation/revision artifacts and any token/time records.
3. Separate one-time development investment, per-commission operating cost, waiting, rework, and unmeasured Human time.
4. Publish only sanitized evidence or digests after privacy/proprietary-content review; never upload raw proprietary strategy code, private paths, credentials or restricted data by default.

## A approval detail verified from underlying registers (2026-10-18 review)
- Original `research_register_approved_v1.json` records 5 discovered sources; only `SRC-A-003` has `verification=VERIFIED`, `operator_decision=APPROVE`, and document verification evidence. Four others remain `PENDING`/`NOT_VERIFIED`, **not** explicit REJECT decisions.
- `a_to_b_release_v1.json`: state `RELEASE`, reason `HUMAN_APPROVED_AND_VERIFIED`, exactly one released source `SRC-A-003`; document SHA-256 `2f46c6c053afeb048ba0ed54444bc36cf14e13808604ea9ab6c651e80ae01a3d`; register SHA-256 `b32bef938a3590406e53f0275669efba01b43ef46d3ac11163cb6e972c9d0cf0`.
- Governance denominator: 1/5 admitted into B. This establishes bounded source release, not scientific validity or XAUUSD M1 generalisability. Source assessment token usage is present in approved register but billing/total A costs are not yet reconciled.

## B initial formulation — original register verified
- 2026-10-13 `20261013T023822439518Z_b_formulate.json` records 3 candidates and SHA-256 `47e987ea3599b9ea1d9d0b9d587d2e0da3256d84c937864450ea8785c2d0a65a` for `candidate_strategy_register_v1.json`.
- Register state `FORMULATED`, model `gemini-3.1-flash-lite`; `CAND-B-001` exhaustion-candle mean reversion, `CAND-B-002` NR7 breakout continuation, `CAND-B-003` pin-bar reversal. All cite approved `SRC-A-003`. These are hypotheses, not approved C releases or demonstrated profitable strategies.
- Recorded initial B usage: prompt 436, candidate output 1384, total 1820 tokens; monetary cost uncalculated. Later B revisions/usage remain to inspect.

## B v1 return and v2 executability — reviewed source records
- `b_v1_return_record.json`: `B_RETURN_FOR_CORRECTION`, `RETURN_TO_B`; all three candidates listed with specification corrections. B owns hypothesis/specification; C owns Stage 1 data, fixed 9-pip friction, execution/evaluation configuration, optimization, and performance testing. B withheld from XAUUSD M1 CSV, Stage 1 results, MT5/OOS data, and performance rankings.
- CAND-B-001: clarify absolute body/range mathematics, remove execution cost/latency assumptions, define timezone. CAND-B-002: resolve volume input vs OHLC proxy, clarify market-open language, remove execution assumptions. CAND-B-003: absolute body, pivot tolerance, remove execution assumptions.
- `b_v2_executability_check.json`: state PASS; 3/3 v2 candidate executability checks PASS, zero failures recorded. **Not** C performance PASS or evidence of strategy qualification.
- Cost impact: revision and governance work exists; elapsed Human time, revision token usage and money remain unmeasured until separate logs inspected.

## B v2 revision resource evidence — reviewed 2026-10-18
- `20261013T025324682438Z_b_v2_revise.json` reports `gemini-3.1-flash-lite`, three candidates, output `candidate_strategy_register_v2.json`, SHA-256 `89fb05814bdcb9d15c2409683b5a0429336e71835db7ea51373b7e83c81e0cae`.
- v2 register state `REFORMULATED_AFTER_RETURN`, linked to v1 register and return record hashes. All three candidate specs revised; no claim of C performance qualification.
- v2 recorded tokens: 1628 input + 1265 output = 2893. v1: 436 input + 1384 output = 1820. Combined recorded formulation/revision = 4713 tokens, of which 2893 (~61.4%) belong to revision. Excludes separate governance-check usage and unmeasured Human effort. API dollars not calculated.

## B v2.1 clarification and B-to-C release — original records reviewed
- `20261013T030011093163Z_operator_clarification.json`: `RECORDED`; parent v2 SHA-256 `89fb05814bdcb9d15c2409683b5a0429336e71835db7ea51373b7e83c81e0cae`; frozen v2.1 SHA-256 `be2ad7c4ec6ee868a9f4d42e94a49dc0f31523539da7cc81d2890e8b54c4a410`; `performance_evidence_seen=false`. This records a clarification operation, but is not itself a signed independent Human decision.
- `b_to_c_release_v2_1.json`: `RELEASE_TO_C`, research commission XAUUSD M1 Price Action, three candidates `CAND-B-001`, `CAND-B-002`, `CAND-B-003`, all v2.1, frozen register SHA matching above.
- Recorded B information boundary excludes Stage 1 CSV, backtest results, MT5/OOS evidence and performance rankings. C owns Stage 1 data, mandatory 9-pip friction, evaluation settings, bounded search and performance/risk calculations. A declared boundary in the record is not proof of enforced filesystem permissions.
- Release means permission to enter C for implementation/testing; no performance PASS, D authority or commissioning follows.

## B v2.1.1 frozen consistency correction — reviewed source records
- `candidate_strategy_register_v2_1_1_frozen.json`: `CLERICAL_CONSISTENCY_CORRECTED_FROZEN`, Human Operator authority dated 2026-10-13, reason `FROZEN_SPEC_INTERNAL_MISMATCH`; no performance evidence seen. CAND-B-002 remaining NR7 references changed to bounded NR-N, and hardcoded breakout entry value replaced by existing `breakout_buffer` parameter. Explicitly no hypothesis, bounds, source or C evaluation-condition changes.
- `b_to_c_release_v2_1_1.json`: `RELEASE_TO_C`, 3 candidates (B-001/B-002/B-003) all v2.1.1, frozen register SHA-256 `2d757b7d2dbcb7f623ac7c0fde68fa74e71915107912fa2ba9e7329c12883e01`; B had no performance evidence and C retains evaluation authority.
- v2.1.1 register repeats v2 token usage 1628/1265/2893. **Do not double-count** as a new API request absent independent request evidence. Additional Human review time unmeasured.

## A search and assessment operation logs — reviewed 2026-10-18
- `20261012T145108721087Z_search.json`: kind `search`, output `research_register_v1.json`, reported SHA-256 `5786c8c979c386d4b09e6f32b8c44a4ff87c0a1739d3a3d79637549870471b96`, source_count 5.
- `20261012T145308631086Z_assess.json`: kind `assess`, output `research_register_assessed_v1.json`, reported SHA-256 `6419bd97570fdcf1dbf7382959d5219dba38b2cfb5eb4a869dffdb7d81d62730`, source_count 5.
- Neither operation log contains token consumption, API price, or elapsed time. Research search API costs remain unknown. Underlying assessment register required to reconcile model usage and avoid treating `totalTokenCount` as input+output only (it may include reasoning tokens).

## A assessment token ledger — assessed register reviewed
- `research_register_assessed_v1.json`, model `gemma-4-26b-a4b-it`, 5 assessed source entries. Per-source (prompt, candidate output, thoughts, reported total): SRC-A-001 (337,96,537,970); SRC-A-002 (1043,121,771,1935); SRC-A-003 (1092,135,676,1903); SRC-A-004 (445,102,711,1258); SRC-A-005 (1259,120,719,2098).
- Sum: 4176 prompt + 574 candidate output + 3414 thoughts = **8164 reported total tokens**. This is assessment model usage only; not Perplexity search API charges.
- B v1 1820 + B v2 2893 = 4713 recorded tokens. Combined A assessment + B initial/revision = **12877 recorded tokens** across these specific operations. Do not infer total A→C bill or cost savings. Source assessment register has `DISCOVERED_NOT_VERIFIED` status at that point; later approval is separately evidenced.

## User-provided pricing scenario and A search endpoint (2026-10-18)
- User-supplied Gemini 3.1 Flash-Lite paid tier: USD 0.25/1M input tokens, USD 1.50/1M output tokens (thinking included). Preview model assumed same rate **provisionally**, not independently verified. Semantic repair assumed Flash-Lite pending model confirmation.
- User states locally hosted `gemma-4-26b-a4b-it` has zero incremental model API charge; local infrastructure cost remains unmeasured.
- Estimated B v1: 436 input + 1384 output = $0.002185; B v2: 1628 + 1265 = $0.0023045; B total $0.0044895. One C build: 1555 + 2030 = $0.00343375. If all 15 build summaries reflect separately billed calls: $0.05150625 **conditional**. Twelve reported repairs: 24732 + 7344 = $0.017199 **conditional**. Conditional B+C sum $0.07319475; excludes Perplexity, Human, infrastructure and other unrecorded usage. No actual invoice checked; avoid claiming paid totals.
- Both `gate2_build_v02A/research_a.py` and `gate2_build_v02B/research_a.py` specify standalone `https://api.perplexity.ai/search`. v02B sends `query` and `max_results`, with no explicit `search_type`. User-supplied standalone rate card: fast $0.001/request, standard $0.005/request. For **one recorded search event**, price scenario $0.001–$0.005 depending on API default; actual billed tier/request count unverified. No source basis to select exact rate.

## Retrospective Human requirements and architecture work (user report 2026-10-18)
- Before/alongside Operator implementation, Human researched CPC evaluation criteria, broker 2,000-activity limit, MT5/Python environment setup and verification, and n8n as an automation option; n8n was not selected. Reasons for non-selection and durations are **not yet documented**.
- Treat as upfront domain discovery, requirements/constraints, technical setup and architecture evaluation, not per-candidate execution or measured manual baseline. Prior ~28 h active estimate applies only to recent week of broad project activity and cannot be apportioned accurately to these tasks without further estimates.
- No measured equivalent manual end-to-end workflow, so do not claim quantified labor savings or ROI.

## Human architecture decision and W9.1 economics draft
- User's retrospective reason for rejecting n8n: too complex for available local models to implement/configure; Python scripts and CLI easier and offer more direct control; C onward must execute locally. No n8n comparative benchmark or quantified savings.
- Draft cost summary: A Gemma assessment 8164 locally hosted tokens, $0 incremental model API charge (compute unmeasured); Perplexity standalone search $0.001-$0.005 per request conditional on default search type; B 4713 recorded tokens and ~$0.0044895 estimated model API; C 15 build records, conditional ~$0.05150625 if separately billed; 12 semantic repairs 32076 reported tokens, conditional ~$0.017199; B+C combined conditional ~$0.07319475. C Stage 1 2184.2s (~36.4 min). Human recent-week retrospective ~28 active hours across broad project work, NOT one run. D/E sandbox costs unmeasured. No demonstrated manual productivity savings or complete per-candidate cost.

## D synthetic sandbox timed demonstration (user console, 2026-10-18)
- Command: `py -c "import subprocess,sys,time; t=time.perf_counter(); p=subprocess.run([sys.executable,'run_d_sandbox_demo.py'],capture_output=True,text=True); print(p.stdout); print(p.stderr); print('EXIT_CODE:',p.returncode); print('ELAPSED_SECONDS:',round(time.perf_counter()-t,4))"`.
- Script `run_d_sandbox_demo.py` uses a temporary directory, `TEST` handoff, `C_TEST_FIXTURE` summary, and exactly three synthetic outcome observations (1,-1,1); it calls `d_sandbox.run`, not production D/MT5.
- Observed exit code 0; wall-clock 0.2629 seconds (includes interpreter startup, fixture creation, D execution and cleanup). Output: `D_SANDBOX_PASS`, `WORKFLOW_TEST_FIXTURE`, observation_count=3, deterministic_score=1, checks `c_handoff_valid=true`, `test_fixture_only=true`, `hidden_fixture_present=true`, `production_authority=false`, `advance_to_e_production=false`. Output hidden_dataset_sha256 `6d588394c2bf6557550dba65fb168dac06f609c02cc6da96cac47705392e9a22` (console-reported, not independently rehashed).
- Proof scope: quick isolated governance/functional sandbox demo. **Not** representative D OOS workload runtime, MT5 adapter verification, CSV/MT5 equivalence, real hidden OOS performance, or authority to advance.

## E synthetic commissioning audit timed demonstration (user console, 2026-10-18)
- Isolated temporary-directory test via subprocess Python, `operator_handoff.TEST` D envelope (`FIX-D-001`, `v0`) containing synthetic `D_SANDBOX_PASS` summary, calling `e_sandbox.audit` with `D_SANDBOX_REVIEW` as both required and observed decision marker. This marker is a test fixture, not an independent real Human commissioning approval.
- Observed exit code 0, subprocess wall-clock elapsed **0.1209 seconds** (includes interpreter startup, fixture setup, audit, cleanup). Output `E_COMMISSIONING_BLOCKED_TEST_ARTIFACT`, mode `WORKFLOW_TEST_SANDBOX`, checks `d_handoff_valid=true`, `test_fixture_detected=true`, `required_human_decisions_present=true`; `commissioning_authority=false`, `commissioned=false`, `advance_to_live=false`.
- Scope: successful fail-closed synthetic audit only; no production commissioning, full production runtime, independent OOS qualification or real Human authorization proven. Output observed in user console; no persistent result artifact created by the temporary test.
