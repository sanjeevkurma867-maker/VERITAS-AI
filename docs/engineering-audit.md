# VERITAS AI engineering audit

The app checks claim-level truth, time validity, and subject scope. The release keeps the React dashboard and FastAPI verification endpoints, and adds a four-claim recorded showcase to the two existing examples.

## Verification pipeline

| Stage | Engineering result |
| --- | --- |
| Claim extraction | The existing splitter handles lists, common compound clauses, and ISO and named date anchors. Configured Bifrost can perform structured extraction with an input-quote check. |
| Temporal scope | The backend preserves exact anchored days and checks applicable earlier periods. An unresolved interpretation can still require review when the date is known. |
| Retrieval | Tavily Research supplies live reasoning and citations. The Bifrost route uses Tavily Search excerpts. Search-only fallback exposes those excerpts for manual review. |
| Evidence validation | URLs must match supplied citations. Bifrost references must match a claim’s source ID and retrieved quote. Evidence carries its time role and relationship to the claim’s subject. |
| Comparison and classification | The classifier checks evidence against the stated period and subject. An organization-wide absence can be refuted by a team counterexample. A team’s prior absence establishes only that team’s history. A corroborated current refutation survives weak evidence about the past. |
| Explanation and correction | Reports expose scope and evidence gaps. An outdated claim receives a suggested correction only when the current citation grounds the wording. The transition requires a dated change at the claim’s scope. |

## Release validation

The automated suite exercises all five verdicts, organization and team boundaries, exact dates, conflicting or insufficient evidence, citation and correction checks, provider fallback, the recorded demo, and the OpenAPI response fields. Use the [README](../README.md#tests-and-limitations) for the commands.

| Check | Result |
| --- | --- |
| Unit and API suite | 37 tests passed. |
| Build and startup | Vite built the production dashboard. A fresh Uvicorn instance served the app and OpenAPI schema. |
| Browser | Chrome passed all three examples, timeline and source links, copy and JSON download, verdict filters, loading, invalid-input recovery, keyboard focus, and mobile layout. |
| Tavily Research | The live browser run produced all five expected verdicts. A separate live scope check distinguished the franchise and men's IPL team. |
| Tavily Search | A live run with Research disabled returned cited excerpts for manual review. |

For the December 31, 2024 cutoff, the live verifier marked the franchise-wide zero-title claim **Contradicted** and the men’s IPL zero-title claim **Historically correct**. The undated franchise-wide zero-title claim was **Outdated** with cited earlier and current evidence. The earlier live test exposed a missing cutoff rule. A confirmed occurrence now refutes an explicit “never” claim at a later historical cutoff, with the usual source and subject checks. [2024 WPL final](https://www.wplt20.com/news/article/match-report-tata-wpl-2024-final) · [2025 IPL final](https://www.iplt20.com/news/article/tata-ipl-2025-final-rcb-vs-pbks-match-report)

## Bifrost integration

The local Docker container listens on `127.0.0.1:8080`. Its health endpoint returned 200 and the protected management API returned 401. The service uses mounted configuration storage. Only a setup-token variable was detected in the container among the checked provider and gateway auth names. The app has a Tavily key configured and needs an authorized Bifrost inference credential. Earlier inference returned 401. The current audit used read-only checks and tests with simulated gateway responses. [Bifrost virtual-key documentation](https://github.com/maximhq/bifrost/blob/dev/docs/features/governance/virtual-keys.mdx)

## Limits that matter for judging

- Live reasoning depends on provider latency, credits, and citation quality. Keep the recorded showcase available for a fixed presentation slot.
- Subject tags come from the reasoning provider. Code enforces containment rules on those tags. Ambiguous names, complex language, and incomplete records can still yield **Needs review**.
- Publisher grouping is a heuristic. The cited sources remain available for inspection.
- A live outdated verdict can appear without a correction if the proposed replacement wording cannot be validated against a qualifying current citation.
- Date-selectable verification and whole-answer repair are optional follow-on work. The app delivers claim-specific dates and cited corrections today.
- Live authenticated Bifrost and Groq verification remains the integration blocker.
