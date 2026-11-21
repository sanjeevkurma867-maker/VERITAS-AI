# Geek Room hackathon requirements

Checked the rendered organizer page on November 21, 2026. The target is **Build a Stale-Answer Detector for AI Applications** under AI Agents & Intelligent Systems. The challenge asks for detection of stale claims in AI answers, live web re-verification, and claim-level freshness. Its description explicitly names Tavily and Bifrost. [Official event page](https://hackculture.io/hackathons/ai-global-hackathon)

| Organizer requirement or guidance | VERITAS AI evidence | State |
| --- | --- | --- |
| Working PS06 prototype that detects stale claims | The dashboard separates historical accuracy from outdated wording, and a dated timeline shows what changed. [README](../README.md) | Implemented |
| Live web evidence and claim-level freshness | Tavily Search supplies evidence from live pages. The verifier assigns a freshness value to assessable present-day claims and shows why other scores are unavailable. [Engineering audit](engineering-audit.md) | Implemented with an explicit eligibility rule |
| PS06 wording names both Tavily and Bifrost | Tavily has been exercised live. The Bifrost inference client exists and has mocked tests. The gateway still requires an authorized inference credential. | Specific challenge wording leaves Bifrost compliance unresolved |
| Project title, theme, description, tools, and how AI is used | Enter **VERITAS AI** and select the exact stale-answer statement. The README and pitch describe the problem and verification pipeline. | Content prepared |
| Public GitHub repository with working source and detailed setup | Local Git repository, environment template, setup, API reference, and tests. | Public URL pending owner authorization |
| PPT explaining problem, solution, architecture, and working prototype | [Editable PowerPoint](VERITAS-AI.pptx) and [walkthrough script](pitch.md). | Prepared locally |
| Demo video and deployment | Both optional in the organizer FAQ. The recorded walkthrough runs locally. | Optional |
| Original work, eligible third-party use, and AI disclosure | Local Git history documents the implementation. The README identifies the dependencies, data providers, and development assistance. | Owner should confirm eligibility and disclosure on submission |
| Team membership and official Discord | The organizer lists teams of one to four and requires participants to join the official Discord. | Participant-side confirmation |

## Sponsor and schedule conflicts

The general submission instructions and FAQ allow Tavily-only entries. They also describe a combined entry with a Bifrost problem as primary and a Tavily checkbox, and mention separate entries for separate sponsor projects. The rules section separately says one final project per team. VERITAS AI targets the Tavily PS06 statement. The specific PS06 wording names both integrations, so a Tavily-only entry under PS06 and any second submission need organizer confirmation. [Official event page](https://hackculture.io/hackathons/ai-global-hackathon)

The live round schedule shows prototype submissions ending **November 21 at 11:59 PM IST** and judging on **November 28**. The FAQ lists **November 15** and **November 29**. Use the signed-in submission deadline and current organizer communication to determine the applicable dates. [Official event page](https://hackculture.io/hackathons/ai-global-hackathon)

The observed submission form required theme, problem statement, title, and GitHub fields and showed separate second-project fields. The organizer text independently confirms the PPT requirement and identifies the demo video as optional. The publicly accessible rules permit standard third-party technologies under their licenses and call for disclosure of AI use and reused work. [Official event page](https://hackculture.io/hackathons/ai-global-hackathon) · [HackCulture code of conduct](https://hackculture.io/legal/code-of-conduct)

## Submission description

**VERITAS AI** finds claims in AI-generated answers that were once true and have since gone stale. It identifies each claim’s subject and time scope, retrieves evidence with Tavily, and publishes a claim-level verdict when the source passages justify it. A **Then → Change → Now** timeline explains when a claim stopped applying and links to a grounded correction. Search can still resolve selected claims when Research reaches a quota limit. The Bifrost client is implemented, with authenticated live inference pending. ChatGPT and Codex assisted with development and documentation.

## Judging alignment

The organizer lists innovation, technical execution, problem and potential impact, use of AI, user experience, and scalability and potential. The extra checks below are internal release criteria. [Official event page](https://hackculture.io/hackathons/ai-global-hackathon)

| Area | Current evidence | Remaining weakness | Priority |
| --- | --- | --- | --- |
| Problem relevance and impact | The app detects stale claims and returns cited corrections for use in AI workflows. | No adoption or impact study yet. | P1 |
| Innovation and explainability | The same claim can resolve differently by historical date, and an outdated verdict requires both periods. | Coverage for complex entities and expressions varies. | P1 |
| Technical execution and reliability | Typed verification responses, bounded provider work, expiry-aware retrieval cache, and provider failure regressions. | Deterministic passage checks cover selected claim forms. | P0 |
| Use of AI and tools | Tavily Research provides structured semantic assessments when available. Retrieved source text is checked before citation roles count. | Live Bifrost inference is unverified. | P0 |
| Accuracy | Regression cases distinguish current, historical, stale, contradicted, and uncertain claims. | A regression suite does not establish population-wide accuracy. | P1 |
| User experience and demo | Responsive report, no fake progress, recorded multi-claim showcase, export, and a timed script. | A live request can outlast a fixed demo slot. | P1 |
| Scalability | Bounded concurrency and a short-lived process-local cache reduce duplicate Search calls. | No distributed cache or load study. | P2 |
| Reproducibility | Setup commands, lockfile, OpenAPI examples, and recorded scenarios are available locally. | Public repository URL and PPT upload remain participant actions. | P0 |
