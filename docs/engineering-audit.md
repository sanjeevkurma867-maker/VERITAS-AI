# VERITAS AI engineering audit

## Pipeline and classification

| Stage | Release behavior |
| --- | --- |
| Input and extraction | FastAPI bounds the input and concurrent jobs. The local extractor produces up to five distinct claims. Bifrost can propose structured claim decomposition when authorized. |
| Temporal and subject scope | Explicit dates constrain historical evidence. Relative event windows use the verification date in UTC. Evidence must match the entity and qualifiers, with containment rules for absence and existence claims. |
| Retrieval and fallback | Tavily Search supplies page text. A targeted Search can decide eligible claims before Research. If Research is limited or unavailable, deterministic checks can resolve supported patterns and preserve context for the remaining claims. |
| Citation validation | URLs must originate in provider results. Bifrost quotes must match a claim-specific retrieved passage. Tavily Extract checks Research quotes against cited pages. Unmatched quotes remain contextual. Tracking URL variants and exact syndicated text are grouped before counting independent corroboration. |
| Temporal comparison | **Historically correct** requires evidence for the stated past period. **Outdated** requires a prior valid state and a qualifying refutation today. **Supported today** covers current or stable facts. **Contradicted** requires a refutation for the relevant scope with no established earlier truth for a stale verdict. Missing scope, insufficient evidence and evidence conflicts yield **Needs review**. |
| Explanation and correction | A transition only appears with a qualifying change date. A correction requires qualifying current evidence. The report gives citation provenance, claim freshness, evidence coverage, completeness, warnings and stage timings. |

The earlier Search fallback classified every retrieved source as context. Even when the source described a real change, the classifier received no temporal evidence roles or supported subject relationship. This produced **Needs review** and zero coverage. The updated fallback promotes only proven passage-level relationships and uses the same corroboration, subject and period checks as the other paths.

An IPL win can disprove a franchise-wide assertion of zero trophies. Proving the franchise’s earlier absence requires franchise-wide history. Regressions also enforce the reverse boundary, where organization-level evidence cannot establish a result for a specific team. A prior live Research run distinguished the franchise from the men’s team at a December 31, 2024 cutoff. It marked franchise-wide zero titles **Contradicted**, men’s IPL zero titles **Historically correct**, and undated franchise-wide zero titles **Outdated** with evidence for both periods. In the current Search-only test, “RCB doesn’t have trophy” returned eight contextual sources and remained **Needs review**. The passage rules do not resolve trophy scope or establish the earlier record. [2024 WPL final](https://www.wplt20.com/news/article/match-report-tata-wpl-2024-final) · [2025 IPL final](https://www.iplt20.com/news/article/tata-ipl-2025-final-rcb-vs-pbks-match-report)

## Validation on November 21, 2026

| Check | Result |
| --- | --- |
| Unit and API suite | 57 passed. Zero failed or skipped. Tests cover the five verdicts, source and subject scope, prompt injection, stale caching, source conflicts, provider failures, and malformed or ungrounded model output. |
| Build, backend and API | Vite production build, dev startup and API proxy passed. Fresh Uvicorn served `/health`, `/openapi.json`, and the production dashboard. API tests exercised both demo and live report schemas. |
| Browser | Chromium passed the three recorded scenarios, Then → Change → Now, filters, citation links, copy correction, copy report, JSON export, keyboard focus, invalid-input recovery, loading, and live Search at 390 px. |
| Tavily Search | Actual provider requests returned page-backed verdicts for Python 2 and Mandela. The warm repeat retained the sources’ original retrieval time and marked them cached. |
| Tavily Research and Extract | One live Research probe hit a request or credit limit, so this run could not reach Extract. Tests exercise successful quote grounding, unmatched quotes, unknown URLs, provider outages, and cooldown. The prior release’s live Research results predate this quote-grounding path. |
| Bifrost → Groq | Local gateway health returned HTTP 200. Protected configuration returned HTTP 401. Earlier unauthenticated inference returned HTTP 401. Success, timeout, auth failure and malformed output are simulated in tests. |

### Reported claim cases

| Case | Verified behavior and limits |
| --- | --- |
| A–C · Pluto current and historical states | Recorded scenarios and classifier tests exercise stale, historically correct, and supported current results. The 2006 resolution is the recorded change. [IAU resolution](https://www.iau.org/IAU/Iau/News/PR2006/iau-2006-general-assembly-resolution-votes.aspx) |
| D · Earth has three moons | The earlier observed contradiction uses the conventional permanent natural satellite interpretation. The current reasoning prompt requires stating a consequential interpretation and otherwise retaining uncertainty. No fresh live semantic verdict was run for this exact claim. [NASA Earth facts](https://science.nasa.gov/earth/facts/) |
| E · UK prime minister | Checked independently against government records. As of November 21, 2026, the UK government lists Andy Burnham, in office since July 20, 2026. It lists Rishi Sunak’s tenure as October 25, 2022 to July 5, 2024. This supports the observed obsolete Sunak claim. This release did not rerun the claim through live Research. [Current prime minister](https://www.gov.uk/government/ministers/prime-minister) · [Rishi Sunak](https://www.gov.uk/government/people/rishi-sunak) |
| F and H · Python 2 and Mandela | Live Search returned **Outdated** for Python 2, including the wording naming the PSF, and **Historically correct** for Mandela’s release in 1990. [Python 2 sunset](https://www.python.org/doc/sunset-python-2/) · [Nelson Mandela Foundation](https://www.nelsonmandela.org/news/entry/nelson-mandelas-release-from-prison-33-years-on) |
| G and J · Mixed and competing statements | The live Search-only run used the exact three claims from G plus the RCB shorthand. Python 2 was **Outdated**. Pluto, Earth’s moon count and RCB remained **Needs review**. J was covered by the recorded Pluto cases and classifier tests. Its exact current-versus-current input was not rerun live. |
| I · Sensational claim about yesterday | The relative event parser resolves a UTC day. Missing trustworthy point evidence stays in review. Regression tests cover date mismatches and undated or unsupported passages. |
| K and L · Injection and ambiguous definitions | The suite rejects instruction-only input and injected source passages, and checks unclear scope. Gateway and Research prompts require an explicit interpretation when alternate definitions affect a verdict. The exact geopolitical input was not verified live this run. |

### Measured performance

One controlled local comparison used the same two claims with Research disabled. Timings measure server work and exclude browser overhead. They are individual observations.

| Run | Total | Decisive coverage |
| --- | ---: | ---: |
| Previous fallback, live retrieval | 521 ms | 0/2 |
| Updated fallback, cold Search | 518–1,010 ms | 2/2 |
| Updated fallback, warm Search cache | 28–30 ms | 2/2 |
| Updated fallback, cold qualified Python claim | 273–398 ms | 1/1 |
| Updated fallback, fresh browser process | 529 ms | 2/2 |
| Updated fallback, mixed astronomy, lifecycle and trophy claims | 4,176 ms | 1/4 |

The 518 ms cold run spent 504 ms waiting on Tavily Search and 13 ms on passage checks. The installed Tavily Python SDK was 0.8.5, and the app uses HTTPX for the Search, Research and Extract REST APIs. Cache keys account for credentials via a digest, query, scope and UTC day. Current evidence expires after two minutes and historical or stable evidence after ten. FastAPI records stage timings and counts, omitting claims, provider bodies and credentials. The cache is process-local. Research and Bifrost latency cannot be inferred from the Search measurements.

## Bifrost blocker and limits

The running `veritas-bifrost` container uses a mounted configuration database. Its inspected environment exposed the existence of a management setup token. The image and health response did not report a release version. The backend has no configured gateway credential. The protected endpoint prevented verification of the virtual key’s active provider and model permissions. The client is configured to target `groq/openai/gpt-oss-120b` by default. A successful live response is needed to establish the actual model. The documented `x-bf-vk` header is implemented. [Bifrost virtual keys](https://github.com/maximhq/bifrost/blob/dev/docs/features/governance/virtual-keys.mdx)

Set `BIFROST_VIRTUAL_KEY` in the existing `backend/.env` to an authorized inference virtual key for the running gateway’s Groq model, then restart Uvicorn. An actual report labeled **Tavily Search + Bifrost** is the remaining runtime check. If gateway HTTP auth is also required, the app supports a separate `BIFROST_AUTH_TOKEN`.

Passage rules cover selected English claim forms. Complex entities, conflicting sources, unavailable extracts, and uncertain interpretation can leave claims unresolved. Publisher categories and model judgments about an excerpt’s meaning are heuristic. Checks for source injection are defense in depth. The dashboard shows a real pending request and a completed report, with no per-claim progress stream. Date-selectable audits, broader evidence evaluation and authenticated Bifrost remain follow-on work.
