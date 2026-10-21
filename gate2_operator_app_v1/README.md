# Gate 2 Operator App v1

This is the consolidation step: browser operation for the already-commissioned B return loop.

Copy into a new folder beside `gate2_c_controller`, then also copy these already-tested backend files into this folder:
- b_resume.py v2
- model_endpoint.py
- b_model_adapter.py
- b_resume_model_flow.py

Launch once:
`py gate2.py`

URL:
`http://127.0.0.1:8787/`

The app owns:
- Human decision ledger
- one-active-process dispatcher
- Return/Resume/Retry B
- automatic governed B package -> configured model endpoint -> deterministic validation
- B review surface with Return / Reject / Release to C

Important current boundary:
`Release to C` currently moves the candidate to READY_FOR_C but DOES NOT yet launch C. This is intentional until the existing generic C CLI chain is registered/verified. The app must not invent C processing.

To show the already-generated v2.1.2 release in the review card, copy the existing folder:
`gate2_dispatcher_app_v1\evidence\b_resume\CAND-B-002`
to:
`gate2_operator_app_v1\evidence\b_resume\CAND-B-002`

That is a one-time migration of already-created evidence, not an operating step. Alternatively, use Return to B in the app and it will generate a fresh governed correction automatically.

No new provider is introduced. The model endpoint remains configurable via `gate2_c_controller\.env`. No fallback is used.
