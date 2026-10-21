# MSI5002 Week 5 — Gate 2 factual handover

**Scope:** Week 5 decomposition, W5.1–W5.4, as discussed in this conversation; later W6–W8 documents used only to identify subsequent revisions and limits. **Prepared:** 18 October 2026. **Status:** factual handover, not final Portfolio or Journal. **Gate 2 deadline:** 27 October 2026, 23:59 Singapore time.

## 1. Week and scope

- **W5.1:** Five-workstream map A–E. Initial version preserved; edited version and later `W5v1.4.md` contain the map. Exact creation dates of every intermediate version are not independently established in the conversation.
- **W5.2:** Number Cards A–E designed. Card C was subsequently updated to include a pre-flight check. Cards describe planned measurements, not measured strategy outcomes.
- **W5.3:** Peer challenge to Row C recorded in `W5v1.4.md` (the conversation refers to a v1.3 upload). Peer identity and independent exchange timestamp are not verified here.
- **W5.4:** Dated **1 October 2026**. Decision: retain Row C as a single workstream provisionally; require an internal pre-flight friction check and a synthetic rogue-friction test. The test was proposed, not shown executed.
- Later continuity source: `MSI5002_Working_Record_End_W5.md`; this is an assistant-produced secondary summary, not original evidence.

## 2. Original design

### Endpoint and proof floors from Gate 1

The project aims to identify and commission a modular quantitative trading strategy supporting manual on-screen trade alerts, subject to Human Operator commissioning. The specified gates include **CPC >= 1.2 after a mandatory flat 9-pip transaction penalty**, **maximum drawdown <15%**, **daily broker/server activities <2,000**, **zero Martingale/grid** (later working records also prohibit averaging-down), **zero third-party black-box dependencies**, inspectable/modular code and **at least 100 OOS trades** for the final evidence standard. Exceptional **CPC >2.0 or Sharpe >2.0** triggers Human integrity audit. These are design thresholds, not achieved results.

### W5.1 map

| Row | Workstream | Output / allocation / proof |
|---|---|---|
| A | Research & Source Qualification | AI researcher proposes sources; Human approves source register; approved evidence passes to B. |
| B | Evidence Synthesis & Strategy Formulation | AI prepares grounded candidate hypotheses and specifications; Human accepts permitted candidates; B hands search directions to C. |
| C | Local Integration & Stage 1 Backtesting | Local deterministic integration, optimisation and backtesting under Operator-controlled data/thresholds; Stage 1 evidence and eligible candidate identity pass to D. |
| D | Stage 2 Walk-Forward / OOS Validation | Frozen candidate faces unseen evidence; Human controls OOS isolation; results and identity evidence pass to E. |
| E | Commissioning Audit & Decision | AI summariser may assemble evidence; Human makes commissioning decision. |

Working shorthand adopted during discussion: **B generates hypotheses → C searches → D falsifies → E decides**. The W5 interpretation allowed C to depart from B's starting hypothesis; later W6 design narrowed C to B-approved logic and search ranges, escalating material logic changes back to B.

### W5.2 Number Cards

A measured proposed source-register entries passing qualification; B measured complete/traceable specification fields; C measured mandatory Stage 1 gates; D measured independent OOS validation outcomes; E measured commissioning evidence completeness. All were **Planned**. No quantitative run results were supplied.

## 3. Actual work, tests and outcomes

**Actually produced:** versioned Markdown design records, a five-row map, five Number Cards, a peer challenge, and a dated W5.4 decision. These are documentation artifacts.

**Actual human discussion:** User rejected a proposed research-checklist denominator because no checklist existed; challenged AI's suggestion that C must reproduce B's exact code specification; questioned whether C was too large; accepted deferring any re-cut; and directed W5.4 to justify retaining C with an internal control.

**Actual code executed in this conversation for the Week 5 trading workflow:** **None demonstrated.** No Python pre-flight guard, Stage 1 runner, backtest ledger, dependency scan, MT5 validation or reproducibility run is evidenced.

**Proposed test:** synthetic rogue candidate/configuration with transaction friction **0 rather than 9 pips**, expecting **HOLD before Stage 1 execution**. **Observed result:** not available. **n executed:** not established; do not report a PASS.

**Later W6.3:** ten **paper walkthroughs** T01–T10 of a **different B→C handoff protocol**, documented as 10/10 expected paper routes. They are **not** executable friction tests and do not validate the W5.4 rogue-friction proposal. The W6.3 record explicitly says technical enforcement was not built/tested.

**Monetary run cost:** no actual billed monetary amount or timed run cost is established in the reviewed materials. Do not substitute an estimate or infer zero.

## 4. Operator decisions

| Trigger | Options | Decision and rationale | Consequence / retained Human authority |
|---|---|---|---|
| AI proposed a research-checklist denominator | Invent a checklist; use existing research-register entries | User said **“no i dont have a research checklist.”** Card A revised to measurable register-entry qualification. | Human retains source relevance/approval; Python structural checks only planned. |
| AI proposed strict B→C code/specification conformance | Require exact implementation; permit bounded empirical search | User questioned whether a C strategy differing from B could still be useful if it survived gates. Exact conformance was removed as a Stage 1 gate. | Evaluation conditions remain fixed; later W6 clarified limits on autonomous logic changes. |
| C combined build and backtest | Split into two workstreams; keep one with internal controls | User raised **“C is abit too huge”**; chose to defer structural split until peer challenge. | Original map preserved rather than silently rewritten. |
| W5.3 peer found friction bypass risk | Split C; retain C and add pre-flight | **1 Oct:** retain C provisionally because a missing internal control had been identified, not proof of a wrong workstream boundary. | Human release before backtest in W5.4 proposal; re-cut remains possible if rogue test fails. |
| AI review vs deterministic checking | Agent approves safety; deterministic checks with advisory AI | Discussion favoured deterministic PASS/HOLD/FAIL and optional advisory AI reviewer, not LLM self-approval. | No claim that arbitrary code is proved free of malicious intent. No checker executed. |

## 5. Changes and re-cuts

1. **W5 Card A:** from hypothetical research-checklist coverage to proposed-register source qualification; prompted by user's correction. Date of exchange not independently established.
2. **W5 B→C conception:** from exact code conformance to B hypotheses / C empirical search; prompted by user challenge. Later **W6** constrained C's search envelope. Do not flatten these different historical versions into one timeless rule.
3. **C structural cut:** a six-row alternative (separate candidate build/qualification and Stage 1 backtesting) was discussed, **not adopted**. The five-row map remained.
4. **W5.3 → W5.4, 1 October:** identified missing friction proof; retained C and proposed internal pre-flight + Human release; updated Card C accordingly. **No demonstrated software PASS.**
5. **Later W6 design:** changed from checking a candidate-controlled friction setting to an **Operator-owned harness applying 9 pips total per completed round-trip trade**. This is a subsequent architecture revision, not a W5 test result. W6 notes explicitly say harness arithmetic/implementation was not built.
6. **Later W7:** ordinary B→C Human sign-off was proposed for push-down to governed automatic release; this differs from W5.4/W6.2 Human release and requires effective-rule version reconciliation before implementation.

## 6. Failures, challenges and unresolved limitations

- **Documented vulnerability:** absent/disabled 9-pip penalty might produce CPC in [1.2, 2.0] and evade the >2.0 anomaly trigger. This was a peer's plausible failure hypothesis, **not an observed software failure**.
- **No executed rogue test:** no input file, pre-flight output, HOLD log or actual blocked run supplied.
- **No implemented C:** neither candidate build/integration nor Stage 1 validation is demonstrated complete.
- **No verified dependency/malicious-code screening:** AST/import scanning, sandbox isolation, secrets/network checks and agent review were discussed as future controls.
- **No proven data isolation or reproducibility:** no code hash comparison, frozen dataset manifest or rerun ledger provided.
- **Friction semantics unresolved at code level:** W6 describes total 9 pips per completed round trip; precise accounting across trade records remains to be implemented and tested.
- **W5 versus later W6/W7 authority differences:** should be shown as dated design evolution, not presented as simultaneous executable rules.
- **Peer identity, intermediate version timestamps, and independently executed user checks:** not established by the available record.

## 7. Evidence inventory

| Artifact / location | What it supports | Verification status |
|---|---|---|
| `/mnt/data/MSI5002-Gate1-ChewKokLoong 2.26.09 PM.pdf` | Gate 1 charter, thresholds and original decomposition | Uploaded project file; exact spelling includes narrow space before PM in mount name. |
| `/mnt/data/W5v1.4.md` | W5.1 map, W5.2 cards, W5.3 challenge, W5.4 | Uploaded project file. |
| `/mnt/data/W5v1.4_records.md` | Additional W5 decision history | Uploaded project file; contents should be checked before citing individual claims. |
| `W5v1.3.md` | Intermediate peer-challenge version mentioned in chat | **Not independently verified as a separate mounted file.** |
| `/mnt/data/MSI5002_Working_Record_End_W5.md` | Secondary continuity summary | Created in this conversation; not primary run evidence. |
| `/mnt/data/W6v1.3.md` | Later routing and architecture changes | Uploaded project file. |
| `/mnt/data/W6.3 Test artifacts.md` | Later T01–T10 paper test record | Uploaded project file; no executable enforcement proven. |
| `/mnt/data/W7v1.2.md` | Later approval-boundary redesign | Uploaded project file. |
| `/mnt/data/W8v1.md` | Later endpoint proof bar | Uploaded project file. |
| `/mnt/data/MSI5002 Gate 2 brief (9 Sep 2026) (1).pdf` | Gate 2 Parts 1–7 requirements | Uploaded project file; brief states updated 8 Oct 2026. |
| `preflight_guard.py`, Stage 1 runner, candidate hashes, MT5 logs, rogue test ID | Future implementation/evidence ideas | **No actual filenames/versions/hashes/test logs verified.** |

**Links:** No independently verified public or Project share URL for these specific evidence files is available. The paths above are local project mounts, not public hyperlinks. **Hashes:** none recorded for W5 artifacts. **Sample sizes:** W5 rogue test n not run/unknown; W6.3 paper walkthroughs n=10 scenarios, not executable tests.

## 8. Gate 2 mapping (Parts 1–7)

| Gate 2 part | Supported by W5 evidence | Limit |
|---|---|---|
| **1. Revised Charter** | Human retains capital, threshold, data and commissioning authority; W5.4 decision tests rationale for allocation. | No verified Charter line change arising directly from a software run. |
| **2. Endpoint and proof plan** | Original Gate 1 CPC, friction, drawdown, activity, inspectability and OOS standards; W5 exposed false-PASS risk. | No endpoint threshold demonstrated met. Later W8 provides dated proof bar. |
| **3. Workstream map** | Five-row W5.1, five Number Cards, peer challenge, W5.4 retained-cut rationale. | No operational proof that five-row cut is sufficient. |
| **4. Workflow architecture** | Planned A→E proof chain and C internal pre-flight sequence. | Not an end-to-end workflow shown to run; no real time/money economics. |
| **5. Governance/routing** | Human release, fixed evaluation conditions and HOLD-before-execution concept; later W6 routing elaborates. | No technical trigger observed firing. |
| **6. Engineered-proof dossier** | Testable rogue-friction specification and proposed deterministic checker. | **No executable W5 test result**; paper designs are not in-vivo evidence. |
| **7. What the system got wrong** | Peer identified missing friction control in design; AI's checklist and conformance assumptions were challenged. | Do not describe as a discovered production code failure or successful repair. |

## 9. Claims requiring verification

1. Locate the original W5.1 v1/v1.1/v1.3 artifacts and verify timestamps and precise wording before claiming exact version chronology.
2. Confirm the W5.3 peer's identity/date and retain the original challenge in its original form.
3. Confirm whether any rogue friction=0 test was run **after** the archived W5/W6 notes; require source, command, output and blocked-execution evidence.
4. Verify whether a pre-flight checker, harness or Stage 1 strategy code exists elsewhere; none is proven by this conversation.
5. Verify the exact transaction-cost unit/round-trip arithmetic before stating that 9 pips were applied to a real ledger.
6. Confirm which W6/W7 release rule is active before describing automatic vs Human approval.
7. Verify independent OOS dataset selection and code fingerprinting only from actual files/logs, not architectural prose.
8. Verify actual run expenses and time logs; no measured amount is supplied here.
9. Distinguish AI-generated explanatory examples (sample CPCs, mock PASS outputs, hypothetical schema records) from actual trading or checker results.
10. If citing W6.3, label it **10 paper walkthroughs of W6.2 v1**, not ten software test executions or a test of the W5 friction guard.

---

**Transfer instruction:** This file is a Week 5 handover. Treat uploaded W5 original artifacts as primary; this handover as a secondary index. Preserve the original five-row cut and the 1 October decision, and never upgrade planned tests into observed outcomes without new evidence.