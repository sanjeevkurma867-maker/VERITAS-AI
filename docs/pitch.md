# VERITAS AI hackathon pitch

VERITAS AI checks whether a claim in an AI answer applies to the time and subject it describes. A dated evidence timeline and a cited correction show what changed. The four-claim recorded example gives judges a complete walkthrough in about 80 seconds.

## Slide outline

| Slide | What to show | What to say |
| --- | --- | --- |
| 1. Stale facts in AI answers | Two versions of the Pluto claim, one present tense and one anchored to 2005 | An AI answer can repeat a fact after its validity changes. The same wording can produce a different verdict once the period is explicit. |
| 2. Why time and scope matter | The past claim, the current claim, and a franchise-versus-team example | A fact-check needs to identify both what the claim describes and when it applies. A team’s win can disprove an organization-wide claim of zero wins. The team’s earlier record alone covers only that team. |
| 3. VERITAS AI | The dashboard input and report | Paste an answer and review its individual claims, dates, citations, and suggested corrections. Coverage shows how many claims reached a cited verdict. |
| 4. Temporal Claim Intelligence | Pluto’s Then → Change → Now timeline | Earlier evidence establishes the old state, the IAU resolution dates the change, and current evidence establishes the updated classification. Historical claims are checked against their own periods. |
| 5. Architecture and safeguards | The architecture diagram in the README | React and FastAPI orchestrate retrieval, reasoning, and verification. Tavily Research supplies live assessments. The optional Bifrost route uses Tavily Search excerpts. Code checks citations, dates, subject scope, and corrections before publishing a verdict. |
| 6. Demonstration | **Four claims, four verdicts** and its report | Show an outdated claim, a historically correct claim, a stable supported claim, and a contradicted claim in one answer. Then show the source and copy the correction. |
| 7. Impact and future work | An AI assistant that attaches VERITAS AI’s report to an answer | Knowledge-base assistants, educational tools, and fact-sensitive workflows can flag claims that deserve a refresh. Next steps include evaluating more domains, richer date-window handling, and an authenticated gateway pilot. |

## 80-second walkthrough

| Time | Action and narration |
| --- | --- |
| 0–12 seconds | Show the workspace. “If an AI says Pluto is the ninth planet, the answer sounds plausible because it once held. In 2005, that wording describes a different period.” |
| 12–24 seconds | Open **Four claims, four verdicts**. Point out the **Recorded example** label and the **Outdated** and **Historically correct** badges. “The time each claim asserts determines which evidence can decide it.” |
| 24–48 seconds | Walk through **Then**, **Change**, and **Now**. Point to the IAU’s 2006 decision and the current classification citation. Click **Copy correction** and show its confirmation. [IAU resolution](https://www.iau.org/IAU/Iau/News/PR2006/iau-2006-general-assembly-resolution-votes.aspx) |
| 48–66 seconds | Scroll to the two Python claims. “The same citation supports Guido van Rossum’s authorship and refutes the James Gosling attribution.” [Python FAQ](https://docs.python.org/3/faq/general.html#why-was-python-created-in-the-first-place) |
| 66–80 seconds | Show **Copy report** and **Download JSON**. “An AI team can review exactly which claims need a refresh and carry the citations forward.” |

Use the recorded report for the timed walkthrough. Start a separate live job before the presentation, then show its provider label and citations when it finishes. The dashboard identifies both modes.

## Integration talking points

Tavily Search and Tavily Research are available for live use with the configured key. The local Bifrost gateway is reachable. End-to-end Groq inference requires authorized gateway access, so describe that route as implemented and exercise it live only after authorization succeeds.

[Architecture and local setup](../README.md) · [Engineering evidence and limitations](engineering-audit.md)
