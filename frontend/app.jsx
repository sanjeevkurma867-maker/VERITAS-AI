import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

const LIMIT = 6000;
const VERDICTS = {
  outdated: "Outdated",
  historically_correct: "Historically correct",
  current: "Supported today",
  contradicted: "Contradicted",
  needs_review: "Needs review",
};
const SCOPES = {
  current: "Present-day claim",
  historical: "Historical claim",
  stable: "Stable fact",
  future: "Future claim",
  unclear: "Unclear time frame",
};
const PIPELINES = {
  bifrost: "Tavily Search + Bifrost",
  tavily_research: "Tavily Research",
  tavily_search: "Tavily Search · evidence only",
  tavily_search_rules: "Tavily Search · passage checks",
  recorded: "Recorded example",
};
const EVIDENCE_LABELS = {
  historical: "Past evidence",
  change: "Change evidence",
  current: "Current evidence",
  retrieved: "Retrieved sources",
};
const TRANSITION_LABELS = { historical: "Then", change: "Change", current: "Now" };
const SOURCE_TYPES = {
  official: "Official publisher",
  institutional: "Institutional publisher",
  reference: "Reference or news publisher",
};
const RELATIONS = { supports: "Supports", contradicts: "Refutes", context: "Context" };
const SUBJECT_SCOPES = { narrower: "Narrower scope", broader: "Broader scope", different: "Different scope", unclear: "Scope unconfirmed" };
const number = new Intl.NumberFormat();
const date = new Intl.DateTimeFormat(undefined, { dateStyle: "medium" });
const dateTime = new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" });

function displayDate(value) {
  if (!value) return "";
  const normalized = /^\d{4}-\d{2}-\d{2}$/.test(value) ? value + "T00:00:00" : value;
  const parsed = new Date(normalized);
  return Number.isNaN(parsed.getTime()) ? value : date.format(parsed);
}

function displayTime(value) {
  if (!value || /^\d{4}$/.test(value)) return value || "";
  return /^\d{4}-\d{2}-\d{2}$/.test(value) ? displayDate(value) : value;
}

function claimScope(claim) {
  return claim.recent_event ? "Recent event · UTC" : SCOPES[claim.time_scope];
}

function Badge({ status, children }) {
  return <span className={`badge ${status}`}>{children || VERDICTS[status]}</span>;
}

function TimelinePreview() {
  return (
    <div className="timeline-preview" aria-label="Pluto classification example">
      <span className="preview-title">Pluto’s classification</span>
      <ol>
        <li><span>THEN · 2005</span><strong>Ninth planet</strong></li>
        <li><span>CHANGE · 2006</span><strong>IAU reclassification</strong></li>
        <li><span>NOW</span><strong>Dwarf planet</strong></li>
      </ol>
    </div>
  );
}

function Intro({ inputRef }) {
  function focusInput(event) {
    event.preventDefault();
    inputRef.current?.focus();
  }
  return (
    <section className="hero" aria-labelledby="page-title">
      <div className="hero-copy">
        <p className="eyebrow">Temporal Claim Intelligence</p>
        <h1 id="page-title">AI answers have an <span>expiration date.</span></h1>
        <p className="hero-description">Find the claims that went stale. See what was true, what changed, and which sources back the update.</p>
        <a className="hero-link" href="#answer" onClick={focusInput}>Verify an AI answer</a>
      </div>
      <TimelinePreview />
    </section>
  );
}

function Workspace({ answer, setAnswer, busy, error, run, inputRef }) {
  return (
    <div className="workspace">
      <section className="panel input-panel" aria-labelledby="input-title">
        <h2 id="input-title">Check an AI answer</h2>
        <p className="description" id="input-hint">Paste an answer or a few claims. Include dates where they matter.</p>
        <form id="verify-form" onSubmit={(event) => { event.preventDefault(); run(); }}>
          <label htmlFor="answer" className="visually-hidden">Answer or claims</label>
          <textarea id="answer" ref={inputRef} value={answer} onChange={(event) => setAnswer(event.target.value)}
            minLength={3} maxLength={LIMIT} required readOnly={Boolean(busy)} aria-describedby="input-hint"
            placeholder="Paste an AI-generated answer…" />
          <div className="input-meta"><span>Up to 5 claims per check</span><span>{number.format(answer.length)} / {number.format(LIMIT)}</span></div>
          <button className="button primary" id="verify-button" type="submit" disabled={Boolean(busy)}>Verify claims</button>
        </form>
        {busy && <p className="message progress" id="progress" role="status"><span className="spinner" aria-hidden="true" />{busy}</p>}
        {error && <p className="message error" id="error" role="alert">{error}</p>}
      </section>
      <aside className="panel examples-panel" aria-labelledby="examples-title">
        <h2 id="examples-title">Example scenarios</h2>
        <p className="description">Open a recorded report with source citations.</p>
        <button className="example-button" id="mixed-example" disabled={Boolean(busy)} onClick={() => run("mixed")}>
          <span className="example-icon astronomy" aria-hidden="true">◈</span>
          <span><strong>Four claims, four verdicts</strong><small>Pluto’s timeline and Python’s authorship</small></span>
        </button>
        <button className="example-button" id="example-button" disabled={Boolean(busy)} onClick={() => run("pluto")}>
          <span className="example-icon astronomy" aria-hidden="true">◉</span>
          <span><strong>Pluto reclassification</strong><small>Past accuracy and an outdated claim</small></span>
        </button>
        <button className="example-button" id="python-example" disabled={Boolean(busy)} onClick={() => run("python")}>
          <span className="example-icon software" aria-hidden="true">⌘</span>
          <span><strong>Python 2 support</strong><small>Software sunset and mixed verdicts</small></span>
        </button>
      </aside>
    </div>
  );
}

function Source({ source }) {
  const quality = SOURCE_TYPES[source.quality];
  return (
    <div className="source">
      <div className="source-meta">
        {source.event_period && <strong>{displayTime(source.event_period)}</strong>}
        {source.role !== "retrieved" && <span>{RELATIONS[source.relation]}</span>}
        {source.role !== "retrieved" && SUBJECT_SCOPES[source.subject_relation] && <span>{SUBJECT_SCOPES[source.subject_relation]}</span>}
        {quality && <span>{quality}</span>}
        {source.grounding === "page_passage" && <span>Page passage matched</span>}
        {source.cached && <span>Cached evidence</span>}
      </div>
      <p>{source.snippet}</p>
      {source.excerpt && source.excerpt !== source.snippet && (
        <details className="excerpt"><summary>View source excerpt</summary><blockquote>{source.excerpt}</blockquote></details>
      )}
      <a className="source-link" href={source.url} target="_blank" rel="noopener noreferrer">{source.title}</a>
      {source.published_date && <small className="publication">Published {displayDate(source.published_date)}</small>}
      {source.retrieved_at && <small className="publication">Retrieved {displayDate(source.retrieved_at)}</small>}
    </div>
  );
}

function Evidence({ claim }) {
  const groups = Object.keys(EVIDENCE_LABELS).map((role) => ({
    role,
    label: claim.has_transition ? TRANSITION_LABELS[role] : EVIDENCE_LABELS[role],
    sources: claim.sources.filter((source) => source.role === role),
  })).filter((group) => group.sources.length);

  if (!groups.length) return <p className="no-evidence">No cited evidence for this claim.</p>;

  return (
    <section className="evidence-section">
      <h4>{claim.has_transition ? "What changed?" : claim.time_scope === "stable" ? "Source evidence" : "Evidence timeline"}</h4>
      <ol className={`evidence-grid ${claim.has_transition ? "transition" : ""}`}
        style={{ "--columns": groups.length }}>
        {groups.map(({ role, label, sources }) => (
          <li key={role} className={`evidence-group ${role}`}>
            <h5>{claim.time_scope === "stable" && role === "current" ? "Reference evidence" : label}</h5>
            <Source source={sources[0]} />
            {sources.length > 1 && (
              <details className="more-sources">
                <summary>{sources.length - 1} more {sources.length === 2 ? "source" : "sources"}</summary>
                {sources.slice(1).map((source) => <Source key={source.url + source.relation + source.subject_relation} source={source} />)}
              </details>
            )}
          </li>
        ))}
      </ol>
    </section>
  );
}

function ClaimCard({ claim }) {
  const [copyState, setCopyState] = useState("");
  const freshnessReason = claim.time_scope === "historical" || claim.time_scope === "stable"
    ? "Freshness applies to assessable present-day claims."
    : "Freshness requires a verdict of Supported today or Outdated for a present-day claim.";
  async function copyCorrection() {
    try {
      await navigator.clipboard.writeText(claim.updated_claim);
      setCopyState("Correction copied");
    } catch {
      setCopyState("Clipboard unavailable. Select the correction to copy it.");
    }
  }

  return (
    <article className="panel claim-card">
      <div className="claim-meta">
        <Badge status={claim.status} />
        <span>{claimScope(claim)}{claim.claim_period ? ` · ${displayTime(claim.claim_period)}` : ""}</span>
        <span className="claim-freshness" title={claim.freshness_score === null ? freshnessReason : undefined}>
          Freshness {claim.freshness_score === null ? "unavailable" : `${claim.freshness_score}/100`}
        </span>
      </div>
      <h3>{claim.claim}</h3>
      {claim.interpretation && <p className="claim-explanation"><strong>Interpretation</strong> {claim.interpretation}</p>}
      <p className="claim-explanation">{claim.explanation}</p>
      {claim.updated_claim && (
        <div className="updated-claim">
          <div>
            <h4>Suggested correction</h4>
            <p>{claim.updated_claim}</p>
            <a href={claim.correction_url} className="source-link" target="_blank" rel="noopener noreferrer">Correction source</a>
          </div>
          <div className="correction-actions">
            <button className="button secondary" onClick={copyCorrection}>Copy correction</button>
            <span className="action-feedback" role="status">{copyState}</span>
          </div>
        </div>
      )}
      <Evidence claim={claim} />
    </article>
  );
}

function formatReport(report) {
  const lines = [
    "VERITAS AI verification report",
    `${PIPELINES[report.pipeline]} · ${report.checked_at}`,
    `Freshness: ${report.summary.freshness.score ?? "Unavailable"}`,
    `Evidence coverage: ${report.summary.evidence_coverage.assessed}/${report.total_claims}`,
    `Verification: ${report.verification.replaceAll("_", " ")}`,
  ];
  for (const warning of report.warnings) lines.push(warning);
  for (const claim of report.claims) {
    lines.push("", `[${VERDICTS[claim.status]}] ${claim.claim}`, claimScope(claim) + (claim.claim_period ? ` (${claim.claim_period})` : ""), claim.explanation);
    lines.push(`Claim freshness: ${claim.freshness_score ?? "Unavailable"}`);
    if (claim.interpretation) lines.push(`Interpretation: ${claim.interpretation}`);
    if (claim.updated_claim) lines.push(`Suggested correction: ${claim.updated_claim}`, claim.correction_url);
    for (const item of claim.sources) {
      lines.push(`- ${item.title} (${EVIDENCE_LABELS[item.role]}${item.event_period ? `, ${item.event_period}` : ""}${item.cached ? ", cached evidence" : ""})`, item.snippet, item.url);
    }
  }
  return lines.join("\n");
}

function Summary({ report }) {
  const { freshness, evidence_coverage: coverage } = report.summary;
  return (
    <div className="metrics">
      <div className="metric">
        <h3>Answer freshness</h3>
        <div className="metric-value">{freshness.score === null ? "Unavailable" : <>{freshness.score}<small> / 100</small></>}</div>
        {freshness.score !== null && <progress aria-label="Answer freshness" value={freshness.score} max="100" />}
        <p>{freshness.scored
          ? `${freshness.current} of ${freshness.scored} assessable present-day claims still hold.`
          : "Requires a supported or outdated present-day claim."}</p>
        {freshness.unscored_current > 0 && <p>{freshness.unscored_current} present-day {freshness.unscored_current === 1 ? "claim omitted" : "claims omitted"} from freshness.</p>}
      </div>
      <div className="metric">
        <h3>Evidence coverage</h3>
        <div className="metric-value">{coverage.percent ?? 0}<small>%</small></div>
        <progress aria-label="Evidence coverage" value={coverage.percent ?? 0} max="100" />
        <p>{coverage.assessed} of {coverage.total} claims reached a cited verdict.</p>
      </div>
      <div className="metric">
        <h3>Claims evaluated</h3>
        <div className="metric-value">{report.total_claims}</div>
        <p>{report.summary.verdicts.needs_review} need review.</p>
        {report.omitted_claims > 0 && <p>{report.omitted_claims} beyond the five-claim limit.</p>}
      </div>
    </div>
  );
}

function Report({ report, previous }) {
  const heading = useRef(null);
  const [filter, setFilter] = useState("all");
  const [feedback, setFeedback] = useState("");

  useEffect(() => { heading.current?.focus(); }, []);

  async function copyReport() {
    try {
      await navigator.clipboard.writeText(formatReport(report));
      setFeedback("Report copied");
    } catch {
      setFeedback("Clipboard unavailable. Download the report as JSON.");
    }
  }

  function downloadReport() {
    const blob = new Blob([JSON.stringify(report, null, 2) + "\n"], { type: "application/json" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "veritas-report.json";
    link.click();
    window.setTimeout(() => URL.revokeObjectURL(link.href), 1000);
  }

  return (
    <section className="report" id="report" aria-labelledby="report-title">
      <div className="report-heading">
        <div>
          <h2 id="report-title" tabIndex={-1} ref={heading}>Verification report</h2>
          <p id="report-meta" className="description">
            {previous ? "Last completed report · " : ""}
            {PIPELINES[report.pipeline]}{report.scenario ? ` · ${report.scenario}` : ""}
            {report.mode === "live" ? ` · Checked ${dateTime.format(new Date(report.checked_at))}` : ""}
          </p>
          {report.inference_model && <p className="description model-name">{report.inference_model}</p>}
          {report.verification !== "complete" && <p className="description">{report.verification === "partial" ? "Partial verification. Some claims need review." : "Verification incomplete. Review the retrieved evidence and gaps."}</p>}
          {report.mode === "live" && report.timings_ms.total !== undefined && <p className="description model-name">Request time {(report.timings_ms.total / 1000).toFixed(1)}s</p>}
        </div>
        <div className="report-actions">
          <button className="button secondary" onClick={copyReport}>Copy report</button>
          <button className="button secondary" onClick={downloadReport}>Download JSON</button>
          <span className="action-feedback" role="status">{feedback}</span>
        </div>
      </div>
      {report.warnings.length > 0 && (
        <details className="runtime-notes" open={report.verification !== "complete" ? true : undefined}>
          <summary>Verification limitations</summary>
          <ul>{report.warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul>
        </details>
      )}
      <Summary report={report} />
      <div className="verdict-filters" role="group" aria-label="Filter claims by verdict">
        <button className="filter all" aria-pressed={filter === "all"} onClick={() => setFilter("all")}>All claims</button>
        {Object.entries(VERDICTS).filter(([status]) => report.summary.verdicts[status]).map(([status, label]) => (
          <button key={status} className={`filter ${status}`} aria-pressed={filter === status} onClick={() => setFilter(status)}>
            {report.summary.verdicts[status]} {label}
          </button>
        ))}
      </div>
      <div className="claim-results">
        {report.claims.filter((claim) => filter === "all" || claim.status === filter).map((claim) => <ClaimCard key={claim.claim} claim={claim} />)}
      </div>
    </section>
  );
}

function App() {
  const [answer, setAnswer] = useState("");
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [report, setReport] = useState(null);
  const [reportRevision, setReportRevision] = useState(0);
  const inputRef = useRef(null);

  async function run(scenario) {
    const text = answer.trim();
    setError("");
    if (!scenario && text.length < 3) {
      setError("Enter a factual statement to verify.");
      inputRef.current?.focus();
      return;
    }
    setBusy(scenario ? "Opening the recorded example…" : "Waiting for live evidence and verification. This can take a minute or longer.");
    try {
      const options = { signal: AbortSignal.timeout(scenario ? 8000 : 145000) };
      const response = scenario
        ? await fetch(`/demo?scenario=${encodeURIComponent(scenario)}`, options)
        : await fetch("/verify", {
          ...options,
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ answer: text }),
        });
      const result = await response.json();
      if (!response.ok) {
        setError(typeof result.detail === "string" ? result.detail : "The answer could not be verified. Check the input and try again.");
        return;
      }
      if (scenario) setAnswer(result.answer);
      setReport(result);
      setReportRevision((revision) => revision + 1);
    } catch (failure) {
      setError(failure.name === "TimeoutError"
        ? "The verification timed out. Try again shortly."
        : "The report could not load. Check the connection and try again.");
    } finally {
      setBusy("");
    }
  }

  return (
    <>
      <header className="site-header">
        <div className="container header-inner">
          <a className="brand" href="./">
            <span className="brand-icon" aria-hidden="true" />
            <span>VERITAS <strong>AI</strong></span>
          </a>
          <span className="tagline">The Trust Layer for Artificial Intelligence</span>
          <a className="api-link" href="/docs">API reference</a>
        </div>
      </header>
      <main className="container">
        <Intro inputRef={inputRef} />
        <Workspace {...{ answer, setAnswer, busy, error, run, inputRef }} />
        {report && <Report key={reportRevision} report={report} previous={Boolean(busy || error)} />}
      </main>
    </>
  );
}

createRoot(document.getElementById("root")).render(<App />);
