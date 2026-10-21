# API Billing Evidence — 21 October 2026

**Status:** Provider-dashboard screenshots archived in GitHub; billing-to-operation reconciliation remains incomplete.

## Provider-reported values

| Provider | Screenshot scope | Amount (USD) | Evidence classification |
|---|---|---:|---|
| Gemini API | 28 days, 24 September–21 October 2026; All API Keys; All Models | 0.14 | Provider-dashboard reported total |
| Perplexity Search API | User-supplied usage chart through October 2026; exact filter period not visible in cropped screenshot | 0.005 | Provider-dashboard reported total |
| Combined | Non-identical or incompletely identified periods | 0.145 | Arithmetic sum, **not** a verified single-cycle workflow cost |

## Interpretation and limitations

- Both screenshots were supplied in the Gate 2 reporting conversation on 21 October 2026.
- Gemini's screenshot shows a total cost of USD 0.14 and savings of USD 0.00. It covers all keys and models within the selected period, not solely the Operator workflow.
- The Perplexity screenshot shows USD 0.005, but the cropped image does not expose an exact date-range selector or all request-level usage.
- These are actual dashboard-reported charges, **not provider invoices or independently reconciled billing exports**.
- The totals may include non-project usage; the period scopes differ. No claim is made that USD 0.145 is the cost of a complete A→E run.
- Token-derived B/C estimates from W9 are **not additional expenses** and must not be added to the provider totals.
- Free-tier usage, local compute, and Human time are not priced here.
- Original PNG files are now archived in GitHub, with Git blob identity verified. This does not independently authenticate the provider billing account or prove that all charges belong to this project.

## Required follow-up

1. Record independent SHA-256 of each downloaded PNG if needed for final submission.
2. Reconcile billed model usage and workflow request identifiers if available.
3. Update Parts 4, 6, 7 and the appendix with direct image links.

**Governance:** This record is economic evidence only; it does not change A–E advancement or production authority.

## Original screenshot artifacts — GitHub verified

| Provider | GitHub image | Git blob SHA | Source status |
|---|---|---|---|
| Gemini | [geminicost.png](geminicost.png) | `280ee262802fcac685c6282e17b1fdb5bedfe722` | Image bytes retrieved from GitHub; screenshot shows USD 0.14 across all keys/models for 24 Sep–21 Oct 2026 |
| Perplexity | [perplexitycost.png](perplexitycost.png) | `1ba8a0ba4e2474e8e7d899a3cbf7329057cec5cf` | Image bytes retrieved from GitHub; screenshot shows USD 0.005; exact selected date-range not visible |

The two original PNG files are now archived in the submission-facing repository. The blob identifiers verify their Git object identity, **not the original capture provenance or billing-to-operation allocation**. The SHA-256 of the downloaded PNG bytes has not been independently calculated here. Provider-dashboard figures remain subject to the limitations above.
