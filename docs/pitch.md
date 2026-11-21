# VERITAS AI hackathon pitch

VERITAS AI checks whether a claim in an AI answer applies to the time and subject it describes. A dated evidence timeline and a cited correction show what changed. Use the four-claim recorded example for a 105-second walkthrough. [Download the editable PowerPoint](VERITAS-AI.pptx)

## Slide outline

| Slide | What to show | What to say |
| --- | --- | --- |
| 1. Stale facts in AI answers | Two versions of the Pluto claim, one present tense and one anchored to 2005 | An AI answer can repeat a fact after its validity changes. The same wording can produce a different verdict once the period is explicit. |
| 2. Why time and scope matter | The past claim, the current claim, and a franchise-versus-team example | A fact-check needs to identify both what the claim describes and when it applies. A team’s win can disprove an organization-wide claim of zero wins. The team’s earlier record alone covers only that team. |
| 3. VERITAS AI | The dashboard input and report | Paste an answer and review its individual claims, dates, citations, and suggested corrections. Coverage shows how many claims reached a cited verdict. |
| 4. Temporal Claim Intelligence | Pluto’s Then → Change → Now timeline | Earlier evidence establishes the old state, the IAU resolution dates the change, and current evidence establishes the updated classification. Historical claims are checked against their own periods. |
| 5. Architecture and safeguards | The architecture diagram in the README | Tavily Search retrieves source passages. Guarded rules handle eligible claims. Tavily Research can handle deeper questions when quota is available, and Extract checks its proposed quotes. Code checks citations, dates, scope, and corrections before returning a verdict. |
| 6. Demonstration | **Four claims, four verdicts** and its report | Show an outdated claim, a historically correct claim, a stable supported claim, and a contradicted claim in one answer. Then show the source and copy the correction. |
| 7. Impact and future work | An AI assistant that attaches VERITAS AI’s report to an answer | Knowledge-base assistants, educational tools, and fact-sensitive workflows can flag claims that deserve a refresh. Next steps include evaluating more domains, richer date-window handling, and an authenticated gateway pilot. |

## 105-second walkthrough

| Time | Action and narration |
| --- | --- |
| 0–15 seconds | Show the workspace. “When an AI says Pluto is the ninth planet, it repeats a fact that once held. Saying the same thing about 2005 makes a historically accurate claim.” |
| 15–31 seconds | Open **Four claims, four verdicts**. Point to the input, the **Recorded example** label, and the two Pluto badges. “VERITAS AI takes one answer, separates its claims, and checks each against the time and subject it describes.” |
| 31–58 seconds | Follow **Then**, **Change**, and **Now**. Point to the IAU’s 2006 decision and the current classification citation. Click **Copy correction**. “The decision gives us the date the classification changed. The correction keeps the citation.” [IAU resolution](https://www.iau.org/IAU/Iau/News/PR2006/iau-2006-general-assembly-resolution-votes.aspx) |
| 58–75 seconds | Scroll to the Python claims. “The same reference supports Guido van Rossum’s authorship and refutes the James Gosling attribution. These claims do not contribute to present-day freshness.” [Python FAQ](https://docs.python.org/3/faq/general.html#why-was-python-created-in-the-first-place) |
| 75–92 seconds | If the separate live report is open, show its provider label and verified passage. “Tavily Search retrieves the original page text. Here the Python Software Foundation dates the end of Python 2 support, and the historical record dates Mandela’s release.” If offline, use the recorded citation cards and describe the separately verified Search capability. |
| 92–105 seconds | Show **Copy report** and **Download JSON**. “A knowledge-base team can see which claims need a refresh and carry the supporting evidence into its editorial workflow.” |

Use the recorded report for the timed walkthrough. For the optional live preview, open a separate tab and submit `Python 2 is officially supported. In 1990, Nelson Mandela was released from prison.` Show its provider label and citations after the result finishes. The dashboard labels cached passages with their original retrieval dates.

## Integration talking points

Tavily Search produced the two live verdicts in the preview. The current Research probe reached a request or credit limit. The gateway answered its health check, and the earlier inference request returned HTTP 401. The deck identifies Bifrost as awaiting authorized runtime verification.

[Architecture and local setup](../README.md) · [Engineering evidence and limitations](engineering-audit.md)
