# MODEL_HOSTING_INTERCHANGEABILITY_AUDIT

**Scope:** MSI5002 Gate 2 Part 4 §4.3; read-only source/configuration inspection on 22 October 2026. Source snapshot: professor-facing v2 `main` at `83dcb3f` (bundled B/C engines), cross-referenced with working repository `fix/w6-b-governance-controls` at `4399c75` before audit. Actual workstation credentials and historical private provider logs were not inspected.

## Architecture and observed implementation

**Original architectural rationale:** local inference was preferred primarily to **protect proprietary strategy confidentiality and retain Operator control** over restricted specifications, generated code, evaluation and governance. Avoiding API fees was secondary. The intended flow has a local DMR lead/integrator receiving restricted B/C content; only generic GREEN coding commissions should reach an external coding endpoint.

| Dimension | Actual implementation | Evidence and confidence | Status |
|---|---|---|---|
| OpenAI-compatible C client | `gate2_c_controller/c_controller.py:agent/call` posts `{model,messages,temperature}` to `<base>/chat/completions`; optional Bearer header; parses `choices[0].message.content` | Source + mocked `test_c_model_chat_openai_compatible_mock`; no real provider call in this audit | IMPLEMENTED_AND_TESTED (mock only) |
| C endpoint/model configuration | `config/agent_registry.json`: local lead `DMR_BASE_URL`, `DMR_MODEL`, optional `DMR_API_KEY`; external coder `CODING_API_BASE_URL`, `CODING_API_MODEL`, `CODING_API_KEY` | Registry inspection + missing-config fail-closed test | IMPLEMENTED_AND_TESTED (configuration logic only) |
| B endpoint adapter | `gate2_operator_app_v1/model_endpoint.py:endpoint_config/chat` accepts `MODEL_BASE_URL`/`MODEL_NAME`/`MODEL_API_KEY` (aliases `DMR_*`), `MODEL_PROTOCOL`; OpenAI-compatible and Google Generative Language REST shapes | Mocked OpenAI path and unsupported-endpoint denial | IMPLEMENTED_AND_TESTED (mock only) |
| B model route | `b_model_adapter.py` builds a frozen-work-package prompt and calls `model_endpoint.chat`; invalid JSON/endpoint errors HOLD; no fallback | Source inspection; no real model substitution test | IMPLEMENTED_NOT_TESTED |
| C provider substitution | Registry can select any endpoint serving OpenAI-compatible chat-completions schema without changing `c_controller.call` | Architectural inspection; **not** a tested switch between two live providers | IMPLEMENTED_NOT_TESTED |
| A provider substitution | Historical A assessment records reference locally hosted Gemma; standalone Perplexity search also recorded | `w9/W9_1_WORKING_EVIDENCE_2026-10-18.md`; A live routing implementation not established by this audit | IMPLEMENTED_NOT_TESTED |
| D/E model substitution | D/E are local validation/commissioning governance stages, not interchangeable LLM agents in the inspected runtime | No model adapter for D/E established | NOT_IMPLEMENTED |
| DMR/Gemma endpoint setup | `gate2_c_controller/.env.example` gives a local DMR URL and Gemma model example; `dmr_endpoint_adapter.py:test` defines a smoke test | **Example configuration is not proof of a successful call.** W9.1 records five A-source assessments with local `gemma-4-26b-a4b-it` (8,164 reported total tokens); this supports a historical A assessment, not a verified C DMR run | IMPLEMENTED_NOT_TESTED (for C) |
| DeepCoder and Qwen3-Coder attempts | No dated call logs, benchmark records, exact local model identifiers or outcome artifacts located in the audited repositories/W9 record | Historical attempts **unverified**. Do not claim success, failure, latency, VRAM or throughput | NOT_IMPLEMENTED (as verified evidence) |
| Provider fallback | `b_model_adapter.py` explicitly fails on endpoint error and reports `fallback_used=False`; C client has no automatic cross-provider fallback | Source inspection | IMPLEMENTED_NOT_TESTED |
| Local vs external disclosure routing | `c_controller.classify`, `build_candidate_v2.green`, `file_authoritative_build.green` perform lexical GREEN/RED filtering before delegating generic tasks | Mock/static gateway tests for representative terms; no semantic data-loss-prevention audit | IMPLEMENTED_AND_TESTED (limited lexical cases) |
| Enforcement of endpoint trust by data class | Configurable URL accepts caller-chosen host; no destination allowlist, TLS requirement, provider attestation, explicit payload class policy, or sensitive-content egress firewall shown | Source inspection | NOT_IMPLEMENTED |

## What is switchable today

- **B:** An endpoint that conforms to the OpenAI chat schema, or the implemented Google GenerateContent branch, can be selected via local configuration. This is **code-level protocol adaptability**, not proven real-world provider interchangeability.
- **C:** Both the local DMR lead and external coding agent use OpenAI-compatible chat completions with separate environment keys/model identifiers. Different compatible servers are **architecturally** interchangeable, subject to response schema and model behavior.
- **A:** A historical local Gemma assessment is documented, but the audited C/B adapters do not establish a universal A/B/C/D/E provider switch.
- **D/E:** No general LLM provider switch is needed or verified for the sandbox validation/commissioning stages.

## Local model and historical evidence qualifications

The W9.1 record reports five assessed A sources using a locally hosted `gemma-4-26b-a4b-it`, with 8,164 total reported tokens. That is historical usage evidence **as documented**, not a fresh endpoint test or a hardware benchmark. The C `.env.example` references a Gemma DMR model, but a template is not evidence that the model ran successfully. The audited source contains no independently verified DeepCoder or Qwen3-Coder invocation history. Such attempts may exist in separate local logs; their outcomes remain **unknown** here.

## Confidentiality and Operator control: gaps before external disclosure

1. Approve destinations per data class: local restricted specification/code versus external generic GREEN utility only. Require explicit Operator-approved endpoint allowlists and a documented cross-border/provider disclosure decision.
2. Strengthen the lexical gateway with structured provenance, semantic leak review, deny-by-default unknown payloads, bounded outbound payload capture and audit receipts. The existing GREEN classifier is **not** a confidentiality guarantee.
3. Use separate credentials, secret-store/env handling, network egress controls, redacted logs and provider data-retention/training settings review. Do not commit credentials.
4. Bind model identifier, endpoint origin, payload classification, source/spec hash and response hash to each run; independently verify response schema and no unauthorized fallback.
5. Test two real compatible endpoints with the **same synthetic non-proprietary task** before claiming model interchangeability. No live provider calls were made for this audit.
6. Keep frozen B specifications, unreleased code, proprietary trading rules and restricted market/OOS data local unless a separately approved disclosure rule explicitly permits transfer.

**Safe Part 4 claim:** “The C client and B adapter expose configurable model endpoints and support OpenAI-compatible message conventions; a local DMR lead was the preferred confidentiality architecture. Source and mocked tests establish configuration behavior, but cross-provider substitution and full data-disclosure enforcement have not been demonstrated in this audit.”
