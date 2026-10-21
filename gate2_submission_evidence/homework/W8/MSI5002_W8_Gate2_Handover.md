# MSI5002 — Week 8 Gate 2 Factual Handover

**Primary week:** Week 8 — Engineering the Endpoint / W8.1 Endpoint and Proof Plan  
**Prepared:** 18 October 2026 (handover compilation date, **not** a retroactive proof-standard approval date)  
**Source scope:** This conversation, its prior W5–W7 decisions as recounted here, and the locally available Project artifacts listed in §7.  
**Status:** Historical/evidentiary handover, **not** a Gate 2 Portfolio or Journal entry. No source files or code were modified.

**Evidence vocabulary:** **DESIGNED** = documented rule or intended system; **PAPER-TESTED** = synthetic walkthrough of a written rule; **EXECUTED** = a program or actual trading/data workflow ran with verifiable outputs; **REVISED** = a documented design decision changed; **NOT VERIFIED** = execution/independent review not evidenced. An AI-generated result is not automatically a Human-performed check.

## 1. Week and scope: exercises completed, versions and dates

- **W8.1 Box 1 — Endpoint:** drafted and expressly accepted in this conversation (the discussion identified **12 October 2026** as the working date). The endpoint text appears in `W8v1.md` without an embedded signed approval or `Set on` field.
- **W8.1 Box 2 — What Would Prove Me Wrong:** five failure conditions F1–F5 recorded in `W8v1.md`. The conversation contains earlier, superseded F1–F5 variants. The Operator asked, *“do we not put the measure numbers into the table?”* and later reported incomplete rendering, *“there is only 1 F1?”*; AI regenerated the table. The current file's F1–F5 text, not the earlier chat summaries, is the current documented design.
- **W8.1 Box 3 — Proof bar:** five proposed P1–P5 lines are recorded in `W8v1.md`, specifying thresholds and timing. **No explicit `Set on` date is embedded in the source file.** The conversation proposed 12 October 2026, but this handover does **not** certify the standard was irrevocably fixed before a real run.
- **W8.1 AI attack / classmate break test:** the professor's exercise calls for both. No actual completed cold-read or three-question break-test record for W8.1 is verified here.
- **Week 8 endpoint event record and Journal entry:** not supplied as completed standalone artifacts. This handover must not be mistaken for them.
- **W7.3 Week-Away Test:** explicitly reported by the Operator as not yet done during the W8 transition. No later completion record established.
- **Relevant earlier versions:** `W5v1.4.md`, `W5v1.4_records.md`, `W6v1.3.md`, `W6.3 Test artifacts.md`, `W7v1.1.md`, `W7v1.2.md`. W6.2 B→C Handoff Protocol **v1, dated 6 October 2026**, was paper-tested. W7 changes were later design revisions, **not** evidence that W6.2 v1 was technically replaced.
- **Teaching/assessment dates:** Week 8 class 7 October 2026; homework intended before Week 9 (14 October); Gate 2 Portfolio deadline **27 October 2026, 23:59 Singapore time**. The updated Gate 2 brief is marked **9 September 2026, updated 8 October 2026**.

## 2. Original design: endpoint, workflow, allocation, governance and proof standards

### 2.1 Original Gate 1 subject and boundary

The fixed subject is a **new modular quantitative trading strategy** with governed development, OOS/walk-forward validation and Human-owned commissioning. Gate 1's broader envisioned endpoint includes real-time screen alerts for manual execution. W7/W8 deliberately narrowed the **immediate A–E proof endpoint** to commissioning, while acknowledging that downstream library operation, screen alerts, subscriber communication/change management and manual execution are **not shown as delivered** by this week's work. This scope difference requires an explicit dated Gate 2 account, not silent substitution of the Gate 1 subject.

### 2.2 W8v1 Box 1 endpoint (verbatim)

> By 30 November 2026, I, Chew Kok Loong, will decide whether to commission exactly one newly developed modular quantitative trading strategy for a research domain, or none, based on independently verifiable out-of-sample evidence demonstrating that the selected frozen strategy meets every precommitted performance, risk, execution and integrity requirement, with its identity and configuration verified before installation into the Approved Strategy Library.

**Status:** approved wording in the conversation; **not an achieved outcome**.

### 2.3 Workflow and allocation inherited from W5–W7

A. **Research & Source Qualification** → B. **Evidence Synthesis & Strategy Formulation** → C. **Local Integration & Stage 1 Backtesting** → D. **Stage 2 Walk-Forward / OOS Validation** → E. **Commissioning Audit & Decision**.

- **A:** AI may propose research; source structural checks may be automated; Human Operator admits legitimate, verifiable, relevant evidence. B is not authorised to substitute unapproved sources.
- **B:** produces an evidenced Candidate Strategy Specification and an authorised search envelope; cannot silently change governing rules.
- **C:** restricted/local integration and adaptive parameter optimisation only inside B's approved strategy logic/search bounds; Operator-owned evaluation settings; **mandatory 9-pip penalty cannot be candidate-controlled**. Stage 1 development OHLC evidence; no access to D's unseen OOS/MT5 evidence.
- **D:** independent validation of frozen candidate/version on authorised OOS evidence; valid FAIL terminates candidate, whereas INVALID/HOLD is a validation-integrity problem, not proof of strategy failure. Once OOS evidence influences redesign, it is consumed for that redesigned candidate.
- **E:** Human Operator compares eligible D-PASS candidates and commissions **exactly one or none**; no mechanical winner formula; selected artifact/configuration must match validated identity.

W7.1 retained Human decisions M1, M3, M4, M5, M6 and **M9/CLOSE**; M2 was pushed down, M7 pushed down/removed, M8 removed. `W7v1.2.md` is the governing *proposed integration design* for those markers. It is **not evidence that revised software/routing was deployed**.

### 2.4 W8v1 Box 2 — falsification cases (faithful summary)

| ID | Predefined disconfirming result | Proposed response |
|---|---|---|
| **F1 OOS performance failure** | No eligible frozen candidate achieves **CPC ≥1.2**, after mandatory **9-pip transaction-cost penalty per trade**, over **≥100 OOS trades**. | Commission none; do not relax CPC/friction or optimise against the same OOS evidence. |
| **F2 Risk or execution failure** | Candidate presented as eligible has **maximum drawdown ≥15%** or **daily broker/server activities ≥2,000**. | Reject; favourable CPC cannot override limits. |
| **F3 Prohibited strategy/dependency** | Numerical PASS candidate contains **any Martingale, grid, averaging-down structure or third-party black-box dependency**. | Reject regardless of performance. |
| **F4 Evidence or identity failure** | OOS PASS cannot be independently verified, or frozen code/configuration differs from the qualifying version. | HOLD/REJECT; require checkable evidence chain. |
| **F5 Commissioning decision failure** | Commission >1 qualifying candidate, choose one without defensible comparison, or commission despite zero fully eligible candidates. | Commission one defensibly selected qualifying candidate or none. |

**Important:** F1 describes absence of a commissionable candidate, not necessarily malfunction of the governance system; **NO COMMISSION** can be correct governance. Earlier chat drafts combined performance, risk and sample count in F1, and treated absence of candidates as F5. **Do not replace the final `W8v1.md` wording with those earlier variants.**

### 2.5 W8v1 Box 3 — proposed proof bar

| ID | Standard and reviewer | Timing |
|---|---|---|
| **P1** | Human Operator checks frozen OOS ledger, CPC, friction and trade count: **CPC ≥1.2 after flat 9-pip penalty per trade, across ≥100 OOS trades**. | Each frozen candidate completing D, before E eligibility. |
| **P2** | Human Operator checks OOS drawdown and daily execution/server logs: **drawdown <15% AND activities <2,000/day**. | D, before E. |
| **P3** | Human Operator checks code, logic and dependencies: **zero Martingale, grid, averaging-down and third-party black-box dependencies**. | Before OOS release and reconfirmed on frozen version presented to E. |
| **P4** | Human Operator checks fingerprints/hashes, configuration and validation records: **100% identity/configuration match**, independent reproducibility/traceability, **zero unresolved integrity defects**. | D completion and before commissioning/installation. |
| **P5** | Human Operator checks complete D-PASS set and signed commissioning record: **exactly one candidate passing P1–P4 or none**; defensible recorded comparison if several pass. | Commissioning decision **by 30 November 2026**, before library installation. |

**Measurement caveats:** The source specifies records to inspect, but does not itself supply an executed OOS trade ledger, an independent checker identity separate from the Operator, a complete reproducibility procedure, a CPC formula implementation, or a hash value. The file contains no signed dated proof-bar freeze.

## 3. Actual work: built, tested or executed; outcomes and sample sizes

| Activity | What is evidenced | Outcome / n | Classification |
|---|---|---|---|
| W8 endpoint and F1–F5/P1–P5 | Textual design saved in `W8v1.md` | 1 documented W8 working artifact; **not a test n** | **DESIGNED** |
| W8 AI critique and iterative drafting | Human rejected competence gate, demanded numerical falsifiers and corrected incomplete presentation | Conversation decisions, not trading outcomes | **REVISED** |
| W8 classmate break test | No recorded classmate answers, date or fixes in supplied evidence | **n not established** | **NOT VERIFIED** |
| W6.3 B→C protocol | Ten synthetic paper walkthroughs T01–T10 against W6.2 v1 | **10/10 paper PASS; 0 software executions evidenced** | **PAPER-TESTED** |
| W5 zero-friction rogue pre-flight | Proposed as a future test | No executed result or log | **PLANNED** |
| Workstream C local harness/optimiser/Stage 1 backtest | Architecture specified; no complete source, command, ledger or actual result verified here | No confirmed C PASS | **NOT VERIFIED / INCOMPLETE** |
| Workstream D OOS/MT5 validation | Architecture and proof standard specified | No confirmed D PASS or FAIL execution | **NOT VERIFIED** |
| Workstream E commissioning and library installation | Decision process specified | No signed decision, installed module or manifest verified | **NOT VERIFIED** |
| HOLD reminders/Telegram | Daily reminder requirement described; T07 simulated elapsed time on paper | No actual message-delivery log | **PLANNED / PAPER-TESTED only** |

**Costs:** No actual monetary API, compute, MT5, broker or labour run-cost record was verified. No actual-versus-estimated cost comparison is supported. **9 pips is a modelled trade-friction requirement, not actual project spend.**

## 4. Operator decisions: triggers, options, rationale, consequences, authority

| Decision / time | Trigger and alternatives | Operator decision and rationale | Consequence / status |
|---|---|---|---|
| **W5/W6 friction governance** (W5 records; W6 design documented by 6 Oct) | Peer identified a candidate with friction disabled could appear to pass CPC without triggering >2.0 outlier review; pre-flight check versus stronger harness authority. | Retain mandatory 9 pips and place friction in Operator-controlled evaluation harness, outside candidate control. W5.4 kept C as one row pending testing. | Design improved; rogue bypass/harness enforcement **not executed here**. Original vulnerability attributed to **peer**, not falsely to Operator-executed discovery. |
| **W7 M7** (W7 work; exact decision day not separately timestamped in source) | AI first recommended KEEP for D's repeat >2.0 CPC/Sharpe Human audit; M5 already covers exceptional C result. | Operator: **“i want to challenge M7, i feel it is true double reliance”**. M7 **PUSH DOWN / REMOVE HUMAN RETURN**; preserve D integrity checks for genuinely new anomalies. | `W7v1.2.md` M7; software routing revision unverified. |
| **W7 M8** | AI first recommended Human CLOSE/RETURN B/RESEARCH GAP→A after D FAIL. | Operator: **“if it failed, why do i want to return to B or A? i do not need to find /force a working one”**. Valid D FAIL ends candidate; any new research is separately commissioned. | M8 **REMOVE** in W7.1; terminal-fail enforcement unverified. |
| **W7 M3 availability** | AI questioned rigid 24-hour Human review SLA; possible remove reminder versus retain alert. | Operator: **“yes 24hrs is not strict. but i sitll want to be reminded daily”**. HOLD persists until explicit decision; initial notice and reminders every 24h; silence never approval. | `W7v1.2.md` W7.2 M3; reminder automation not verified. Note W7.1 M3 still says “Within 24h of HOLD notice,” a **cross-section wording inconsistency** to resolve by dated revision, not silently overwrite. |
| **W7 closing marker** | AI proposed downstream manual execution as CLOSE; Operator challenged post-E change management and scope. | Merge **M9/CLOSE** at Human commissioning one D-PASS or NO COMMISSION. Downstream live alerts/execution outside immediate A–E proof. | `W7v1.2.md`; original broader Gate 1 commitment must be disclosed in Gate 2. |
| **W8 competence gate** (discussion around 12 Oct) | AI proposed making Operator's personal technical comprehension an additional commissioning gate. | Operator: **“it should not because that is a competence question outside of this project”**; competent maintenance personnel can be found/assumed, without adding an unapproved subjective gate. | Not added to W8v1 F1–F5/P1–P5. Human remains commissioning authority. |
| **W8 numerical falsification** (discussion around 12 Oct) | AI provided abbreviated failure categories without numbers. | Operator: **“do we not put the measure numbers into the table?”**; required explicit measurable thresholds. | Revised Box 2 and later `W8v1.md`. |
| **W8 Box 1** (discussion around 12 Oct) | Need one checkable endpoint aligned to W7 M9 and Gate 1. | Operator accepted the proposed commissioning endpoint (“yes ok”). | Endpoint wording in W8v1; not evidence of actual commission. |

**Authority:** The Human Operator retains research admission, exceptions/search expansion, extraordinary C-result integrity judgement and final commissioning. Machine-checkable gates are intended to block invalid candidates without discretionary Human overrides. Delegation of routine B→C PASS at W7 M2 is a **proposed re-cut**, not evidence that W6.2 v1 has been replaced in code.

## 5. Changes and re-cuts: before/after, dates, reasons and evidence

| Change | Before | After | When / support | Implementation status |
|---|---|---|---|---|
| Friction enforcement | Candidate/pre-flight configuration vulnerable to omitted friction | Operator-owned harness applies mandatory 9-pip penalty | W5.3 peer finding → W5.4 / W6.1 design; `W5v1.4_records.md`, `W6v1.3.md` | Not executed/verified |
| C workstream structure | Possible split of C considered | Retain one C workstream, strengthen internal gates pending test | W5.4; `W5v1.4_records.md` | Design decision |
| B→C clean release | W6.2 **v1 (6 Oct)** requires explicit Human release; T06/T07 paper-test this | W7 M2 proposes deterministic ordinary release, exceptions retained | `W6.3 Test artifacts.md` → `W7v1.2.md` | **No v2 executed** |
| D exceptional outlier | W6 D PASS with CPC >2.0 or Sharpe >2.0 returns to Human | W7 M7 removes repeat return; new integrity anomaly still HOLD | `W6v1.3.md`, `W7v1.2.md` | Proposed, untested |
| D valid FAIL | W6 describes Human alert/diagnostic and optional returns | W7 M8 terminates valid FAIL without mandatory rescue | `W6v1.3.md`, `W7v1.2.md` | Proposed, untested |
| M3 time | 24h response could read as decision SLA | 24h **reminder cadence**, not deadline; HOLD continues | W7.2 `W7v1.2.md` | Policy text revised; W7.1 old wording remains |
| Closing decision | Downstream manual live trade decision proposed by AI | M9/CLOSE: one qualifying module or none before library installation | W7.1 `W7v1.2.md`, W8 Box 1 `W8v1.md` | Scope change documented; broader Gate 1 live alerts not delivered |
| W8 proof rows | Early AI table categories too general; intermediate F1–F5 variants | Final F1–F5 and P1–P5 in `W8v1.md` | Conversation around 12 Oct; `W8v1.md` | Written, not validated |

**Date discipline:** Where the source supplies only the teaching week, the precise day of a design decision is **not independently verified**. File-system modification dates are not proof of the date a Human signed a rule. The `W8v1.md` file has no embedded freeze date; do not silently assign it 12 October as a formally pre-registered threshold.

## 6. Failures, challenges and unresolved limitations

1. **9-pip bypass vulnerability:** Peer identified silent omission of friction as a plausible false-PASS route. No rogue candidate was demonstrably run; no proof that the proposed harness blocks it.
2. **W6.3 T09 aggregate-limit finding:** A fourth otherwise-valid candidate is HOLD despite passing candidate-level checks. The aggregate counter must be enforced **in addition to** the acceptance checklist. Paper PASS only.
3. **W6.3 T06/T07 versus W7 M2:** W6.2 v1 missing Human release = HOLD; W7 pushes ordinary release down. The paper-test outcome is historically correct for v1, but the proposed new design needs a **new rule version and regression tests**.
4. **W7 M7 double reliance:** Duplicate Human review at C and D for CPC >2.0 or Sharpe >2.0 removed at design level. No evidence of implemented D integrity anomaly routing.
5. **W7 M8 forced remediation:** Valid D FAIL should terminate candidate, not require return to B/A to force success. No executed D FAIL record here.
6. **M3 timing inconsistency:** W7.1 M3 latest point still states within 24h; W7.2 clarifies daily reminder without a deadline. Preserve both as historical wording; date any correction.
7. **W7.3 peer cold-read:** Not completed/verified in this conversation. No peer answers may be fabricated.
8. **W8.1 break test:** No independent classmate responses or dated corrections verified. AI discussion is not a substitute for the assigned cold read.
9. **W8 proof reproducibility:** No independently run CPC calculation, friction verification, OOS ledger, activity count, code hash, installation manifest or reviewer sign-off supplied.
10. **Workstream C remains incomplete:** Do not claim working Stage 1 harness, optimiser, integrated strategy code or successful C PASS.
11. **No real D/E outcomes:** No real OOS PASS/FAIL or commission is established. W8 F1–F5 and P1–P5 are proof intentions, not outcomes.
12. **Proof-standard timing:** W8 proof bar must be set before the test it judges. Current file does not demonstrate a signed `Set on` date or a test chronology. Any results already seen before its adoption must be labelled **already known**.
13. **Human independence:** P1–P5 mostly name the Human Operator as checker; the professor recommends a reviewer other than the producer where possible. No named independent checker is established here.
14. **Potential scope/metric ambiguity:** Gate 1's broad live-alert endpoint is not proven by commissioning a library module. Exact CPC formula, transaction-penalty accounting, broker-activity counting method and OOS window identities are not executable specifications in the Week 8 artifact alone.
15. **Costs:** No actual monetary run-cost evidence or measured baseline is present; no estimated cost should be relabelled actual.

## 7. Evidence inventory: exact artifacts, paths, versions and links

Paths below were **observed in the active container during this handover**. They are local working paths, not public hyperlinks. No Git commit, source-code SHA, trade-artifact hash or independent log checksum was supplied. File existence does **not** authenticate its historical authorship or prove a run.

| Artifact | Verified local path | Content / identifiers | Evidence status |
|---|---|---|---|
| Gate 1 Blueprint | `/mnt/data/MSI5002-Gate1-ChewKokLoong 2.26.09 PM.pdf` | Original project constraints and endpoint | Historical source; path Unicode spacing may require directory listing |
| W5 design | `/mnt/data/W5v1.4.md` | W5.1/W5.2 workstream design | Source artifact |
| W5 decision record | `/mnt/data/W5v1.4_records.md` | W5.3 peer 9-pip challenge, W5.4 retain-C decision | Source artifact; not proof of executed rogue test |
| W6 design | `/mnt/data/W6v1.3.md` | W6.1 routing and W6.2 v1 protocol | Source artifact; protocol v1 dated 6 Oct 2026 |
| W6 test record | `/mnt/data/W6.3 Test artifacts.md` | T01–T10 paper walkthroughs, 10/10 paper PASS | Paper-tested only; technical implementation explicitly “Not built / not technically tested” |
| W7 earlier draft | `/mnt/data/W7v1.1.md` | Earlier W7 integration draft | Historical version |
| W7 revised | `/mnt/data/W7v1.2.md` | W7.1 M1–M9/CLOSE, W7.2 six readiness rows and Charter Box | Current documented W7 design |
| W8 working file | `/mnt/data/W8v1.md` | Box 1 endpoint; F1–F5; P1–P5 | **Designed; no embedded `Set on` date or actual results** |
| Week 8 lecture | `/mnt/data/[For Canvas] MSI5002 Week 08 - Engineering the Endpoint.pptx.pdf` | Official Week 8 teaching | Instruction source |
| Week 8 homework guide | `/mnt/data/MSI5002 Week 8 homework guide (1).pdf` | W8.1 instructions, break test, record/Journal requirements | Instruction source |
| Week 8 study guide | `/mnt/data/MSI5002 Week 8 study guide - medical journals registration rule.pdf` | Pre-registering proof before the run | Teaching reference |
| Gate 2 brief | `/mnt/data/MSI5002 Gate 2 brief (9 Sep 2026) (1).pdf` | Updated 8 Oct 2026; seven Portfolio parts and grading | Authoritative assessment source |
| Professor example | `/mnt/data/Professor toy making gate2.pdf` | Example evidence/audit structure | Teaching example, not project execution |

**W6.3 test identifiers:** `T01_Ordinary_Release.md`, `T02_Ambiguous_Spec.md`, `T03_Grounding_Failure.md`, `T04_Missing_Resource.md`, `T05_Black_Box_Dependency.md`, `T06_Missing_Human_Release.md`, `T07_Human_Silence.md`, `T08_Corrected_Version.md`, `T09_Aggregate_Limit.md`, `T10_Rule_Change_Attempt.md`. These are named evidence sections/records within `W6.3 Test artifacts.md`; **standalone files with these names were not independently verified**.

**Run identifiers, executable commands, trading datasets, hashes and monetary invoices:** none independently verified in the reviewed W8 materials. **External hyperlinks:** no stable share links to project-specific W5–W8 artifacts were supplied; do not invent them. The official Gate 2 form URL is in the brief but is a submission destination, not evidence of a submitted artifact.

## 8. Gate 2 mapping — how the findings support Parts 1–7

| Gate 2 Part | Grounded contribution | Missing/limit |
|---|---|---|
| **Part 1 — Revised Charter** | W7.2 Charter Line 3 held under integration review; Human commissioning and exception authority retained; W8 competence gate rejected. | Formal full seven-line Charter/change log and dated sign-offs not in W8v1. |
| **Part 2 — Venture endpoint and proof plan** | **Primary W8 output:** Box 1 endpoint, F1–F5 falsifiers, P1–P5 proof bar, proposed 30 Nov decision. | Dated `Set on`, actual met/missed/moved record, independent W8 break test, executed results. |
| **Part 3 — Workstream map** | W5 A–E decomposition; retained C and proposed Number Cards; proof cycles from W5. | Actual measured node numbers/baselines not established here. |
| **Part 4 — Workflow architecture** | W7 Human-return integration and W6 routing; M2/M7/M8 re-cuts. | End-to-end executable workflow, tools/capabilities, actual per-run time/money, independent cold-read evidence. |
| **Part 5 — Governance and routing in practice** | W6.2 v1 and W6.3 T01–T10 paper test record; W7 governance revisions. | Live enforcement and real triggers not established; must label paper tests as such. |
| **Part 6 — Engineered-Proof Dossier** | W8 specifies future inspectable ledgers, hashes, logs and gate thresholds; W6 synthetic cases can be labelled in-vitro **paper walkthroughs**, not software runs. | Actual artifact/code, execution proof, n, reproducibility, in-vivo evidence absent. |
| **Part 7 — What the system got wrong** | W5 peer-identified friction loophole, W6 T09 aggregate-counter integration finding, W7 double reliance/forced-remediation/availability findings. | Do not claim these were actual trading-system failures; record design/paper-test level and costs as unknown. |

The updated Gate 2 brief assigns **15/100** to endpoint/proof standard (Part 2), **25/100** to workflow architecture (Parts 3–4), **15/100** to governance (Part 5), **30/100** to engineered proof (Part 6), and **15/100** to Operator judgement (Parts 1 and 7). These weights are assessment guidance, not proof of work performed.

## 9. Claims requiring verification / retrospective interpretation

1. **Formal proof-bar adoption date:** The chat refers to 12 October 2026, but `W8v1.md` has no `Set on` field. Verify an original dated frame/version and whether any relevant results were already known.
2. **Actual W8 classmate break test:** Obtain reader identity/role, date, verbatim answers to “passes but wrong,” “fails but right,” and “either way,” plus dated fixes. No completion assumed.
3. **W7.3 completion:** No evidence supplied; explicitly mark not recorded unless a real peer record is found.
4. **W6 rule supersession:** Find a separately versioned W6.2 revision implementing W7 M2, M3, M7 and M8, or continue to call them **proposed**. Do not rewrite the 6 October v1 paper-test outcomes.
5. **Friction enforcement:** Require executable harness, fixed 9-pip configuration, test ledger, zero-friction adversarial input and execution log before claiming protection.
6. **OOS reproducibility:** Require dataset identity/window, frozen code/parameters, trade count, metric formula, friction application, independent recalculation and hashes. None present here.
7. **Commissioning:** Require signed Human decision and installation manifest before claiming any E outcome.
8. **C implementation:** Confirm actual source files, run commands and logs from the separate implementation environment if any. This conversation's planning record cannot establish completion.
9. **Cost:** Obtain actual usage logs/invoices and time measurements; otherwise state **not measured**. Keep forecasts/estimates separate.
10. **Operator-versus-AI checks:** The Human's documented challenges to M7, M8, M3 and W8 wording are real conversational interventions; W6.3 “observed” routes are written paper evaluations, not proven independent Human software checks.
11. **W8 current wording:** `W8v1.md` has different F1–F5 structure from several intermediate AI answers; quote the file for the current standard and preserve chat variants as superseded drafts.
12. **CPC/friction terminology:** The final file says a **flat 9-pip transaction penalty per trade**; earlier conversation described **9-pip round-trip friction**. Verify the intended unit and calculation implementation before execution; do not silently treat an unresolved arithmetic definition as tested.
13. **Independent reviewer:** P1–P5 name the Human Operator; the Week 8 guide encourages independent checkers where possible. No second reviewer or sign-off is evidenced.
14. **Scope:** Commissioning into the Approved Strategy Library is not proof of operational downstream screen alerts, subscriber change management or live execution. Explain the narrowed immediate endpoint against Gate 1 with a dated reason.
15. **File provenance:** Paths verified in the working container are not public hyperlinks; historical file hashes, commit IDs and source timestamps were not supplied. Do not invent them.

---

### Handover bottom line

**What exists:** A W8.1 written endpoint and falsification/proof plan (`W8v1.md`), grounded in W5–W7 architecture and explicit Human decisions, plus W6.3's **10 synthetic paper walkthroughs**.  
**What does not follow from this evidence:** A technically executed 9-pip harness, completed Workstream C, OOS-qualified candidate, commissioned module, live-alert product, independent W8 classmate break test, or actual monetary cost.  
**Next evidentiary action:** Preserve original W8v1, verify the actual date the proof bar was fixed, obtain the real W8 break-test record, and separately link any genuine implementation logs from outside this conversation before making execution claims.