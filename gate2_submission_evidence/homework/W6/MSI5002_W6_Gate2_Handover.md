# MSI5002 — Week 6 Gate 2 Factual Handover
**Scope:** W6.1 Routing Overlay, W6.2 B→C Handoff Protocol, W6.3 synthetic paper walkthroughs; Week 5 antecedents and later Week 7/8 changes identified but not backdated.  
**Prepared:** 18 October 2026. **Portfolio deadline:** 27 October 2026, 23:59 Singapore time.  
**Evidence standard:** A stated plan, AI-authored walkthrough, independently performed test, and live technical execution are distinct. **No C/D/E trading-strategy validation or commissioning is evidenced here.**

## 1. Week and scope: exercises, versions, dates
- Course Week 6 session: **16 September 2026**; Week 6 homework guide released **22 September 2026**; work discussed/consolidated in chat around **5–6 October 2026**. Do not backdate the actual work to class.
- **W6.1:** five-row A–E Routing Overlay developed and locked by Operator in a project source referred to in chat as `W6v1.1.md`; the available local consolidated file is `W6v1.3.md`. Exact creation/version transition chronology between these filenames is **NOT VERIFIED**. Rows A–E specify input/output classes, environments, next recipients, withheld information, and stop points.
- **W6.2:** `B→C Handoff Protocol v1`, explicitly **dated 6 October 2026**, plus `B→C Acceptance Checklist v1`; one ten-field rule. Original W4.4 Reviewer Test was lost; the Field 7 reviewer sentence was **reconstructed**, not recovered verbatim from Week 4.
- **W6.3:** ten synthetic cases **T01–T10**, with a master test record. The file `W6.3 Test artifacts.md` is present. The record calls the method **paper walkthrough using synthetic inputs**. No actual B→C software run is established.
- Course minimum for W6.3: ordinary case plus at least one failure case, expected outcome recorded before observed outcome, evidence pointer, result and fix/layer. Ten scenarios were chosen by the Operator's stated preference for impact/importance-based coverage, not because ten were required.
- **Later context, not Week 6 outcomes:** `W7v1.1.md` / `W7v1.2.md` propose pushing routine B→C PASS release down to a governed checker and treating 24 hours as a reminder cadence rather than a strict decision deadline. Whether W6.2 was formally revised/retested to reflect those later decisions is **NOT VERIFIED**.

## 2. Original design: endpoint, workflow, allocation, governance, proof
### Endpoint and fixed standards
The Gate 1 direction was a modular quantitative trading strategy supporting **real-time manual-screen execution alerts**, not autonomous live trading. Later design refined E to commission one frozen executable module per research domain into an **Approved Strategy Library**, which a downstream live recommendation screen consumes. The Human Operator retains manual execution and commissioning authority.
Precommitted target/constraints referenced in the sources include:
- **CPC ≥1.2** after **9-pip total transaction friction** (later W8 source describes a penalty per trade; exact round-trip accounting remains an implementation question).
- **Maximum drawdown <15%**; **daily broker/server activities <2,000**; **≥100 OOS trades** in the refined proof plan.
- Zero Martingale/grid/averaging-down and zero third-party black-box dependencies.
- **CPC >2.0 or Sharpe >2.0** as an exceptional-result integrity-review trigger in W6 design.
- These are **planned test thresholds**, not observed trading results.

### W6.1 routing and authority
| Row | Intended work / handoff | Data class / environment | Stop or human control |
|---|---|---|---|
| **A — Research & Source Qualification** | Public research; full Research Evidence Register; only Operator-approved source list and Operator-downloaded documents to B | Public / open processing | Failed verification or Operator rejection held; insufficient evidence may recommission A |
| **B — Evidence Synthesis & Strategy Formulation** | Uses approved A evidence only; creates candidate specifications; no independent retrieval; released specifications to C | Public / open processing | Grounding, data, dependency, specification problems → HOLD; Operator RELEASE / RETURN / REJECT |
| **C — Local Integration & Stage 1 Backtesting** | Integrates with proprietary trading modules, optimises parameters, records all tests; frozen Stage 1 PASS variants to D | Mixed inputs governed Restricted / local; frozen OHLC development dataset; **no MT5/OOS access** | Stage 1 gates, integrity checks; exceptional CPC/Sharpe triggers; no self-expanded search |
| **D — Stage 2 OOS Validation** | Frozen C-PASS code/config; same fixed unseen OOS window for cohort via controlled MT5 interface | Restricted / local | PASS / FAIL / INVALID-HOLD distinct; complete diagnostics; valid D PASS eligible for E |
| **E — Commissioning Audit & Decision** | Compare D survivors; Human commissions **one or none**; exact artifact integrity check before library replacement | Restricted / local-human | No commission permitted; mismatch BLOCK; downstream screen separate |

Other W6 design choices: A research commission bounded by domain; up to **30 candidate sources** in A; B seeks **three feasible candidates**; C can optimise within B's search envelope, with maximum parameter-variant count **not yet set**. Every Stage 1 PASS variant, including weaker PASSes, should proceed to D. C uses Operator-prepared OHLC; D uses MT5 unseen data; shared API concept was **not built**. The Operator-owned harness should apply the 9-pip cost instead of candidate code controlling it; harness was **not built**.

### W6.2 protocol v1 — ten fields
1. **Purpose:** only clear, testable, permitted ideas enter C; performance decided later in C/D.
2. **Boundary:** one Human-approved, versioned Candidate Strategy Specification (logic, model, inputs/outputs, approved-source references, assumptions, parameter ranges, dependencies) crosses; underlying reports, rejected ideas, ranking history withheld.
3. **Permitted work:** capable, available, authorised, resourced; missing obtainable dependencies HOLD; prohibited black boxes do not cross.
4. **Acceptance:** complete specification, grounding, resources, human release; implementation-affecting ambiguity HOLD.
5. **Trigger:** any missing/unclear/failed/unapproved required check.
6. **Response:** all PASS → RELEASE; otherwise HOLD before C and alert Operator; RETURN/REJECT/authorised resolution; corrected version retained alongside held original.
7. **Human decision:** reconstructed sentence names Chew Kok Loong, Telegram, review within 24h, continued HOLD on silence, reminder every 24h until explicit decision.
8. **Aggregate limit:** **maximum three released B candidates per research commission** without a new Human decision.
9. **Record:** every attempt and decision in project folder; Telegram is notice channel, **not** authoritative log.
10. **Change authority:** only Human Operator changes the rule, with dated reason and preserved prior version; B/C may flag but not change it.

## 3. Actual work: created, paper-tested, executed
**Actually produced in conversation/project:** W6.1 written routing decisions; W6.2 v1 written protocol and acceptance checklist; synthetic scenario specifications and written walkthrough outcomes; W6.3 master record. The user requested retained evidence artifacts and explicit pointers. `W6.3 Test artifacts.md` is present in the project files.

**W6.3 case ledger** (all reported outcomes are **AI-authored paper outcomes**, not independently executed system outcomes):
| ID | Synthetic input / issue | Expected written route | Recorded paper outcome | Evidence status |
|---|---|---|---|---|
| T01 | Complete, approved ordinary candidate | RELEASE to C | PASS / RELEASE | Synthetic paper |
| T02 | “use an appropriate lookback period” instead of bounded range | HOLD; C must not guess | PASS / HOLD | Synthetic paper |
| T03 | `SRC-X-099` absent from approved A sources | HOLD grounding failure | PASS / HOLD | Synthetic paper |
| T04 | Legitimate `Library Z` unavailable | HOLD; Human resolves resource | PASS / HOLD | Synthetic paper |
| T05 | Available but prohibited black-box `Service X` | HOLD, Human RETURN/REJECT | PASS / HOLD | Synthetic paper |
| T06 | All technical checks PASS but no Human release | HOLD | PASS / HOLD | Synthetic paper |
| T07 | No Human decision at +24h and +48h | HOLD; daily reminder due | PASS / HOLD | **No actual Telegram delivery** |
| T08 | T02 held v1 returned, corrected v2 | Retain v1; recheck and potentially RELEASE v2 | PASS / simulated v2 RELEASE | Synthetic recovery |
| T09 | Fourth otherwise-valid candidate after three releases | HOLD unless Human authorises exception | PASS / HOLD; implementation finding | Synthetic aggregate |
| T10 | B tries to change rule without Operator approval | No rule change; current v1 governs | PASS / denied | Synthetic authority |

The master record states **10 PASS, 0 FAIL, 0 UNDETERMINED**, where the denominator is **10 AI-authored paper walkthrough scenarios**, **not** ten independent executions, trading tests, or real candidate transfers. The chat does not independently verify that expected results were immutable before AI wrote observed results. **Independent human execution sample size: NOT VERIFIED. Actual technical B→C execution sample size: 0 evidenced. Real C/D/E trading runs: 0 evidenced.**

**No evidence of:** real OHLC/MT5 test run; strategy CPC or drawdown measurement; live Telegram notification/reminder; implemented file permissions; real code hashes/fingerprints; actual candidate admitted to C; D OOS PASS; E commissioning or live-library installation.

## 4. Operator decisions: trigger, alternatives, rationale, authority
| Trigger / human words (chat) | Options / AI initial position | Human decision and rationale | Consequence / evidence |
|---|---|---|---|
| “Why do you say this? ... datasource is controlled ... script running backtesting ... Who sees OOS evidence?” | AI initially recommended **C→D** as consequential because of OOS exposure | Challenged anthropomorphic/overstated contamination premise; frozen deterministic D runner is not C learning OOS results | AI acknowledged and recommended **B→C** instead; W6.2 governs B→C. No claim C→D needs zero controls |
| “Even if a bad strategy pass the test, is it bad?” | AI initially framed B→C as excluding bad strategies | B→C must assess whether an experiment is clear, feasible, permissible and grounded, **not predict its profitability** | C/D retain empirical performance role |
| “If there is any ambiguity, hold and alert the human operator...” | AI proposed allowing some declared testable uncertainty to proceed | Implementation-affecting ambiguity must HOLD; Human decides RETURN to B or resolves within authority | W6.2 Fields 4–6; synthetic T02 |
| “we would need to define this checklist eventually ya” | AI suggested umbrella failure trigger | Required a concrete checklist rather than vague trigger | B→C Acceptance Checklist v1 |
| “turn around should be 24 hours ... telegram ... official notice channel?” and “reminder will keep coming every day” | AI initially proposed silence → HOLD only | Added Telegram notice and daily reminder, silence never approval | Reconstructed W4.4 / Field 7; T07 paper scenario; delivery unimplemented |
| “Yes it will be sitting inside a project folder” | AI suggested separating notification and audit log | Authoritative audit in project folder, Telegram for notices | W6.2 Field 9 |
| “nope, again flag to me, i will decide” | AI asked whether B/C may propose rule changes | B/C flag only; Operator alone decides change | Field 10; T10 paper scenario |
| “we also need to keep artifact of the test ... quote them and make reference” | AI initially discussed representative tests | Required retained paper evidence and references | Synthetic T01–T10 and master record |
| “look at the critical pieces to test from impact and importance pov, not numbers” and “A->B and B->C are more complicated...” | AI suggested three B→C cases | Risk/impact-based coverage of materially different routes; begin with B→C | AI proposed 10 cases; Operator authorised continuation. **A→B comprehensive suite not evidenced** |
| “is the professor expecting us to test in actual setup alreadY?” | AI proposed paper tests | Requested clarification of course evidence standard; accepted paper walkthrough as allowable | No real technical test inferred |

**Human authority** includes source admission, B→C exceptions and aggregate exceptions, search/strategy boundary changes, E commissioning one/none. **Caution:** ordinary B→C Human release was mandatory in W6.2 v1, while later W7 materials propose automating clean releases. Do not blend these versions.

## 5. Changes and re-cuts: before → after
| Before | After | Date / reason | Proof |
|---|---|---|---|
| W5 concern: candidate code could omit 9-pip friction; preflight detection | W6 intended **Operator-owned friction harness** separate from candidate code | W6 design discussion, exact date not independently established; remove ability to bypass via candidate-controlled settings | Design only; harness and bypass test not run |
| AI proposed W6.2 **C→D** handoff | Govern **B→C** | Approximately 5–6 Oct; Operator challenged assumption that deterministic D OOS runner “sees” evidence as an optimiser | W6.2 v1 dated 6 Oct |
| AI initially allowed some declared testable uncertainty | Implementation-affecting ambiguity **HOLD + Operator** | W6.2 design around 6 Oct; prevent C silently designing strategy | W6.2 Fields 4–6; T02 paper |
| AI initially suggested ~3 representative tests | Risk-based coverage of materially distinct B→C routes | W6.3 discussion, around 6 Oct; Operator objected to choosing count rather than impact | T01–T10 paper record |
| Original W4.4 wording lost | Reconstructed named Reviewer Test, Telegram, 24h, repeated reminders | 6 Oct; reconstruction **not original recovered Week 4 text** | W6.2 Field 7 |
| W6.2 candidate checklist PASS could coexist with Field 8 aggregate HOLD | T09 recorded need for separate aggregate check in future implementation | AI identified after synthetic T09; Operator did **not** visibly independently discover it | T09 PASS with implementation finding; **no W6.2 v2** in Week 6 record |
| W6.2 routine B→C Human release | Later W7 materials propose pushing clean release to checker, keeping exceptions human | **Later Week 7**; not to be retroactively assigned to W6 | `W7v1.1.md`, `W7v1.2.md`; formal W6.2 revision/retest NOT VERIFIED |
| W6.2 reviewer decision within 24h | Later W7.2 says no strict decision deadline, 24h reminders while HOLD | **Later Week 7**; conflict must be reconciled | W7.2 text; active protocol NOT VERIFIED |

## 6. Failures, challenges and unresolved limitations
- **No paper FAIL** recorded among T01–T10. This is not evidence that the implementation works. The synthetic cases were authored and evaluated in the same AI conversation, with no verified independent execution or blind review.
- **T09 finding:** candidate-level PASS is insufficient for final release if aggregate limit is exceeded; separate commission-level check must be enforced. This was **AI-identified**, not independently Operator-discovered in visible chat. Written Field 8 already stopped the candidate; no v2 was issued.
- **Human silence and notifications:** T07 simulated +24h/+48h; no Telegram messages or scheduler execution evidenced.
- **No real source-verification or grounding software:** T03 used declared synthetic source IDs, not actual research-source lookup.
- **No actual version-retention mechanism:** T08 simulated v1/v2; no write-protection or immutable artifact proof evidenced.
- **No executable handoff permission controls:** folder, access control and automatic gating remain planned.
- **A→B comprehensive tests** were proposed by the Operator but not shown completed in this chat.
- **C/D/E:** no strategy performance, OOS validation, live recommendation screen, or commissioning execution proved.
- **Outstanding design:** C maximum parameter-variant counts, multi-objective weights, exact 9-pip harness, prohibited-strategy detection, market-data API, fingerprint/hash schema, new OOS selection after consumed evidence.
- **Potential retrospective ambiguity:** AI generated both “expected” and “observed” paper sections; the file headings alone do not establish temporal separation.
- **Later governance inconsistencies:** W7 clean-release automation and non-strict 24h decision timing may supersede W6 wording; formal dated revision is NOT VERIFIED.

## 7. Evidence inventory: filenames, paths, hashes, logs, test IDs
**Paths below are local mounted project-source paths confirmed in this working environment, not proof of original creation date, content immutability, or deployment.** Source files have not been modified for this handover.

| Artifact | Verified mounted path / location | Evidential use | Qualification |
|---|---|---|---|
| Consolidated W6 design/protocol | `/mnt/data/W6v1.3.md` | W6.1 A–E, working decisions, W6.2 v1 | Present; original `W6v1.1.md` version transition NOT VERIFIED |
| W6.3 synthetic tests | `/mnt/data/W6.3 Test artifacts.md` | T01–T10 inputs/checklists/expected/observed | Present; paper, AI-authored |
| W5 antecedent | `/mnt/data/W5v1.4.md` | Workstream/number cards and friction challenge | Present |
| W5 decision record | `/mnt/data/W5v1.4_records.md` | W5 re-cut and historical notes | Present |
| W7 later governance | `/mnt/data/W7v1.1.md`; `/mnt/data/W7v1.2.md` | Later authority/timing changes | Present; do not backdate |
| Week 6 homework | `/mnt/data/MSI5002 Week 6 homework guide (PDF).pdf` | Professor's W6.2/W6.3 requirements | Present |
| Gate 2 brief | `/mnt/data/MSI5002 Gate 2 brief (9 Sep 2026) (1).pdf` | Gate 2 Parts 1–7 and evidence standard | Present; brief updated 8 Oct per document |
| Gate 1 submission | `/mnt/data/MSI5002-Gate1-ChewKokLoong 2.26.09 PM.pdf` | Original endpoint / restrictions | Present |
| Journal guidance | `/mnt/data/[Updated Guidance for the Journal] MSI5002 — The Governance and Reasoning Journal.pdf` | Six-field journal standards | Present |
| `T01_Ordinary_Release.md` ... `T10_Rule_Change_Attempt.md` | Named as pointers in master record | Individual test evidence references | **Separate standalone files NOT VERIFIED**; consolidated test file is present |
| Original W4.4 frame | NOT AVAILABLE | Original Reviewer Test | Lost per Operator; reconstructed text not original |
| Real Telegram log, C release log, OOS ledger, MT5 test output, commissioning manifest | NOT AVAILABLE / NOT VERIFIED | Operational proof | Do not claim execution |
| Actual candidate code fingerprint / hashes | NOT VERIFIED | Identity/reproducibility | No real candidate hashes in this record |
| Test IDs | T01–T10 | Ten synthetic B→C routes | See W6.3 consolidated file |
| Web links | Professor Journal form and Gate 2 form appear in source brief | Submission routes, not test proof | Do not present as execution evidence |

**Hashes:** No original historical SHA-256 values were recorded in the conversation for W6.2 v1 or T01–T10 at the time of testing. Computing a hash now would establish only the *current file bytes*, not pre-test freezing; no historical hash is asserted.

**Sample sizes:** W6.3 `n=10` synthetic scenarios in the written master; independently human-executed `n=NOT VERIFIED`; operational technical runs `n=0 evidenced`; trading C/D/E sample `n=0 evidenced`. The `≥100 OOS trades` requirement is a **threshold**, not an observed sample.

## 8. Gate 2 mapping (Parts 1–7)
| Part | What this Week 6 record supports | Limit |
|---|---|---|
| **Part 1 — Revised Charter** | Operator's retained boundaries, changed AI recommendation, no silent delegation | Need dated Charter text/change log, not provided by Week 6 record alone |
| **Part 2 — Venture endpoint and proof plan** | Stage 1/OOS separation, frozen standards, risk/performance constraints, manual-alert endpoint | W8.1 proof bar and actual results must be separately verified |
| **Part 3 — Workstream map** | W6.1 five-row routing elaborates W5.1 A–E responsibilities and proof handoffs | Not evidence the workflow ran |
| **Part 4 — Workflow architecture** | Intended interfaces, environment separation, owners, handoffs and decision states | Implementation, tool economics and real run logs absent |
| **Part 5 — Governance and routing in practice** | W6.1 classifications; W6.2 ten-field rule; synthetic trigger cases; human HOLD/change authority | Paper control tests only; no live trigger or enforcement proved |
| **Part 6 — Engineered-Proof Dossier** | Traceable synthetic test IDs, expected/observed text, evidence inventory | Label **paper/in-vitro conceptual walkthrough**; no technical/in-vivo claim |
| **Part 7 — What the system got wrong** | AI's erroneous/overstated C→D OOS-exposure rationale, corrected handoff selection; T09 integration finding; W5 friction-control re-cut | Do not invent operational failure, financial cost, or independent T09 discovery |

## 9. Claims requiring verification before portfolio use
1. **Source version chronology:** confirm exact `W6v1.1.md` and `W6v1.3.md` relationship, freeze dates and whether tested v1 bytes are preserved.
2. **Expected-before-observed evidence:** establish whether T01–T10 expected routes were actually written/frozen before the observed walkthroughs; AI-generated formatting alone is insufficient.
3. **Human execution:** did the Operator independently follow/check any test? Which IDs, when, with what retained annotations?
4. **Standalone test files:** are `T01_...md` through `T10_...md` real saved files, or only headings inside `W6.3 Test artifacts.md`?
5. **T09 acceptance:** did Operator independently inspect/approve the no-v2 conclusion, or merely accept AI consolidation? Current chat supports the latter only.
6. **W7 supersession:** identify active B→C release rule and 24h cadence, with dated revision and retest if needed.
7. **Actual source and dependency checking:** whether any real source registry, grounding checker, dependency scanner or audit folder has been used.
8. **Telegram:** actual notice/reminder delivery logs and timestamps; currently no proof.
9. **C/D/E actual run:** candidate code hashes, frozen OHLC data, MT5 OOS window, trade ledger, friction calculation, CPC, DD, trade count and commissioning manifest; none evidenced.
10. **Original W4.4:** remains unavailable; label reconstructed W6 sentence honestly.
11. **T09 aggregate counting semantics:** whether returned/replaced candidates consume one of three release slots and how exceptions are authorised; not resolved in the W6 test.
12. **Dates:** individual conversation messages are not all independently timestamped; use the dated W6.2 v1 document (6 Oct) where supported, and label other timing approximate.
13. **Confidentiality:** any real proprietary code, parameters or restricted trading evidence must stay out of shareable Miro/course test materials; use only shareable descriptions/synthetic cases.
14. **Claim scope:** ten paper PASSes show that an AI-applied written rule yielded the expected routes for chosen synthetic examples; they do **not** prove the live system's correctness, robustness, compliance, or endpoint attainment.

---
**Handover conclusion:** Week 6 produced a documented five-row routing design, a dated B→C ten-field protocol/checklist, and ten AI-authored synthetic paper walkthrough cases. The Operator materially challenged the AI's original C→D rationale, tightened ambiguity and human-authority boundaries, and requested impact-based scenario coverage with retained artifacts. The project has **not** shown actual C, D or E strategy execution or independent technical enforcement of the B→C protocol. This is a factual handover for Gate 2 assembly, **not** the final Portfolio.