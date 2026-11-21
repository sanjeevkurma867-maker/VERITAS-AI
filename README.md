# VERITAS AI

**The Trust Layer for Artificial Intelligence**

VERITAS AI detects stale claims in AI-generated answers. An AI answer can repeat a fact that once held as though it still applies. Temporal Claim Intelligence identifies the period a claim describes, checks evidence for that period, and shows the change when a previously correct claim has been superseded.

Paste an answer to get claim-level verdicts, dated citations, evidence-backed corrections, and an exportable verification report. The **Then → Change → Now** timeline makes the difference between outdated wording and accurate history visible. The dashboard keeps the last completed report available during a follow-up request or provider error.

- Review up to five individual claims and see their time scope, verdict, and evidence.
- Follow cited passages through a change and copy the grounded correction.
- Inspect per-claim freshness, answer freshness, evidence coverage, and verification completeness. Copy the report or download its JSON.
- Run three labeled recorded scenarios without API access.

## Screenshots

![VERITAS AI workspace with the Pluto timeline and recorded examples](docs/workspace.png)

![Recorded verification report with freshness, cited transition, and suggested correction](docs/report.png)

## Run locally

Requirements are Python 3.11 or later and Node.js 22.12 or later. The app was tested with Python 3.14. From the project root, install dependencies and build the React dashboard.

```sh
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
npm --prefix frontend ci
npm --prefix frontend run build
```

Use the existing virtual environment if it is already set up. Set `TAVILY_API_KEY` in the process environment or in `backend/.env` for live checks. Then start FastAPI.

```sh
backend/.venv/bin/python -m uvicorn backend.main:app --reload
```

Open [VERITAS AI](http://127.0.0.1:8000/app/) or the [interactive API reference](http://127.0.0.1:8000/docs). The recorded examples run locally. If port 8000 already serves VERITAS AI, use the existing dashboard. To run a second instance, pass `--port 8001` and open `http://127.0.0.1:8001/app/`.

For React development, keep FastAPI on port 8000 and start Vite in a second terminal.

```sh
npm --prefix frontend run dev
```

Open the [Vite development dashboard](http://127.0.0.1:5173/app/).

## Architecture

```mermaid
flowchart LR
    UI["React dashboard"] --> API["FastAPI verification API"]
    API --> Extract["Atomic claims and time scope<br/>Bifrost extraction when configured"]
    Extract --> Search["Tavily Search<br/>source passages and bounded cache"]
    Search --> Gateway["Bifrost OpenAI-compatible gateway, when authorized"]
    Gateway --> Groq["Groq model for structured assessment"]
    Groq --> Validate["Check source quality, quote, scope and effective dates"]
    Search --> Rules["Deterministic passage checks for supported claim patterns"]
    Rules --> Validate
    Extract --> Research["Tavily Research for unresolved claims"]
    Research --> Page["Tavily Extract checks proposed quotes against source pages"]
    Page --> Validate
    Validate --> Report["Verdicts, timelines, metrics and corrections"]
    Report --> UI
```

The stack is FastAPI, Pydantic, HTTPX, React, Vite, Tavily Search, Research and Extract, and an optional Bifrost gateway routing to Groq. The browser calls FastAPI. FastAPI sends selected claims to Tavily and, when configured, sends source excerpts and claim data to Bifrost. API credentials are read server-side. The backend uses Tavily’s REST APIs directly.

| Pipeline shown in the report | How the result is produced |
| --- | --- |
| Tavily Search + Bifrost | The gateway extracts atomic claims and assesses retrieved excerpts. The backend checks structured output, claim-specific source IDs, quoted text, and dates before assigning verdicts. |
| Tavily Research | Research proposes temporal assessments. Tavily Extract retrieves the cited page text so the backend can verify each decisive quote and check the source roles and effective periods. |
| Tavily Search + passage checks | Retrieved page text can resolve eligible lifecycle, dated event, stable attribution, and classification claims. The classification fallback requires an official page that establishes the earlier category, dated reclassification, and present category before it can return **Outdated**. |
| Tavily Search · evidence only | Search supplies context when qualifying evidence or reasoning is unavailable. Claims receive **Needs review** and freshness is unavailable. |
| Recorded example | Source-backed demonstration data exercises the report interface locally. |

### Server configuration

The [environment template](backend/.env.example) lists the supported settings.

| Variable | Purpose |
| --- | --- |
| `TAVILY_API_KEY` | Tavily key for live retrieval and research. |
| `TAVILY_RESEARCH_ENABLED` | Defaults to `true`. Set to `false` to exercise the Bifrost or Search-only path. |
| `BIFROST_BASE_URL` | Enables gateway integration. For local Bifrost use `http://127.0.0.1:8080/openai/v1`. FastAPI sends `POST /chat/completions` under this base URL. |
| `BIFROST_VIRTUAL_KEY` | Optional gateway virtual key sent as `x-bf-vk`. A configured key also enables the default local URL. |
| `BIFROST_AUTH_TOKEN` | Separate bearer token when the gateway requires HTTP authentication. |
| `BIFROST_MODEL` | Defaults to `groq/openai/gpt-oss-120b`. Set this to a model allowed by your gateway. |

When Research returns HTTP 432 or 433, VERITAS AI falls back to Search. It honors a supplied numeric retry interval. Without one, the backend pauses Research for that key until the process restarts. Restart after quota is restored. A temporary HTTP 429 uses a shorter cooldown.

Configure the Groq provider and model in Bifrost, then use a virtual key that grants access to it. A report showing **Tavily Search + Bifrost** with a Groq model confirms that inference returned a structured, excerpt-grounded result. The report discloses fallback on authentication, timeout, or malformed output. The default model follows Groq’s migration guidance for the preferred Llama model. [Groq deprecation guidance](https://console.groq.com/docs/deprecations) [Bifrost virtual-key reference](https://github.com/maximhq/bifrost/blob/dev/docs/features/governance/virtual-keys.mdx)

Use `BIFROST_VIRTUAL_KEY` for inference governance. The gateway can also require a separate authentication credential. Its setup token serves the management onboarding flow. The local container answered its health endpoint, and its management API returned HTTP 401. The app currently has only a Tavily credential configured. Authorization handling is covered by tests with simulated responses. [Bifrost authentication documentation](https://github.com/maximhq/bifrost/blob/dev/docs/features/governance/virtual-keys.mdx)

### Read the report

| Verdict | Evidence required |
| --- | --- |
| Supported today | Sources support the current state or a stable fact. |
| Historically correct | Sources support the claim during its stated past period. |
| Outdated | Sources establish the earlier state and contradict the same proposition today. |
| Contradicted | Sources refute the claim during its relevant period. Prior validity has not been established. |
| Needs review | Scope, evidence coverage, corroboration, or source agreement is insufficient. |

The dated transition requires evidence of a specific change. Effective periods describe when the cited fact applied. Publication dates appear separately when the provider supplies them. A verdict requires a recognized publisher or corroboration from separate publishers. Publisher categories are a heuristic, and readers can inspect the actual citations.

Evidence also has to match the claim’s entity and qualifiers. A team’s win can disprove an organization-wide claim of zero wins. That team's earlier record by itself describes only the team. Evidence outside the claim’s scope is available as context. The API returns `subject_quantifier` for the claim and `subject_relation` for each citation. A bounded Tavily follow-up can clarify missing historical or current evidence while preserving an established verdict.

**Answer freshness** is the percentage of assessable present-day claims that still hold, calculated as `supported current / (supported current + outdated)`. The report shows which claims were counted and any present-day claims excluded from the score. Claim-level freshness is 100 for supported present-day claims, 0 for outdated claims, and unavailable for other results. **Evidence coverage** counts claims with a decisive, validated citation. **Verification completeness** reports whether all, some, or none of the checked claims were resolved. These are descriptive measures. A source’s retrieved date, effective period, and publication date have different meanings. Cached passages retain their original retrieval date and are labeled in the report.

### API

| Endpoint | Result |
| --- | --- |
| `POST /verify` | Accepts `{"answer":"Pluto is the ninth planet."}` and returns a structured report. |
| `GET /demo?scenario=mixed` | Recorded four-claim showcase with a dated transition, correction, and four distinct verdicts. |
| `GET /demo?scenario=pluto` | Recorded Pluto report. This is the default example. |
| `GET /demo?scenario=python` | Recorded Python 2 support report. |
| `GET /health` | Verifies that the FastAPI process is running. |
| `GET /docs` | Interactive OpenAPI documentation for requests and response schemas. |

Requests accept up to 6,000 characters. The report checks the first five distinct candidate claims and counts omitted candidates. FastAPI limits concurrent verifications per process and reports unavailable providers through bounded requests and readable errors.

```sh
curl -fsS 'http://127.0.0.1:8000/demo?scenario=mixed'
curl -fsS http://127.0.0.1:8000/verify \
  -H 'Content-Type: application/json' \
  --data '{"answer":"Python 2 is officially supported. In 1990, Nelson Mandela was released from prison."}'
```

## Demo and submission

VERITAS AI was built for the Geek Room hackathon’s PS06 stale-answer detector challenge. The submission notes record the sponsor requirements and the remaining Bifrost check. [Hackathon requirement checks](docs/hackathon-compliance.md)

Open **Four claims, four verdicts** for the 105-second recorded walkthrough. It pairs Pluto’s present-day and 2005 classifications with one supported and one contradicted claim about Python’s creation. Walk through **Then**, **Change**, and **Now**, show the IAU citation, and copy the correction. The two-claim API example above is the separate live preview. [Timed script](docs/pitch.md) · [PowerPoint](docs/VERITAS-AI.pptx)

## Tests and limitations

```sh
backend/.venv/bin/python -m unittest discover -s backend/tests -v
npm --prefix frontend run build
```

Tests cover all five verdicts, compound extraction, exact dates, organization versus team scope, evidence conflicts, unsupported corrections, gateway response validation, API failures, OpenAPI, and demo metrics. [Engineering audit](docs/engineering-audit.md)

| Local integration check | Result |
| --- | --- |
| Tavily Search | With Research disabled, the live claim “Pluto is the ninth planet in our solar system” returned **Outdated**, 1/1 coverage, and the three cited timeline steps. Earlier live checks also resolved undated historical classification, software lifecycle, and historical event claims. |
| Tavily Research and Extract | The reported Research failure was HTTP 432, the plan usage limit. This pass used mocked Research and Extract responses for quota handling and citation checks. |
| Bifrost → Groq | Local gateway health returned 200. Protected management and earlier inference returned HTTP 401. The backend needs an authorized inference key for a live Groq check. |

- Live reasoning depends on provider access, source quality, and latency. Passage rules cover a limited set of patterns. General claims may need Research or authenticated Bifrost.
- Without configured Bifrost access, extraction uses English sentence and clause rules. Complex clauses and temporal expressions can require manual review. Subject relationships are proposed by the reasoning provider and checked against the claim’s quantifier, so ambiguous entity names still need care.
- Publisher categories are heuristic. A page quote can confirm citation provenance, while judging semantic relevance for open-ended claims still depends on reasoning quality. Some pages return incomplete extracts.

## Attribution

The recorded scenarios cite the International Astronomical Union, NASA, and the Python Software Foundation. The dashboard links to the cited source passages. Implementation and submission materials were developed with assistance from ChatGPT and Codex.

## Roadmap

Priorities are a larger claim-and-evidence evaluation set, stronger temporal interval handling, and a verified gateway deployment. Date-selectable verification and whole-answer repair are follow-on features once historical coverage and correction grounding can be evaluated reliably.
