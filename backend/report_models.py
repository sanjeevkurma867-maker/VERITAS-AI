from typing import Literal

from pydantic import BaseModel

Verdict = Literal["current", "historically_correct", "outdated", "contradicted", "needs_review"]
Pipeline = Literal["bifrost", "tavily_research", "tavily_search", "recorded"]


class Citation(BaseModel):
    title: str
    url: str
    domain: str
    quality: Literal["official", "institutional", "reference", "other"]
    published_date: str | None
    event_period: str | None
    role: Literal["historical", "change", "current", "retrieved"]
    relation: Literal["supports", "contradicts", "context"]
    subject_relation: Literal["same", "narrower", "broader", "different", "unclear"]
    snippet: str
    excerpt: str | None


class ClaimReport(BaseModel):
    claim: str
    status: Verdict
    time_scope: Literal["current", "historical", "stable", "future", "unclear"]
    subject_quantifier: Literal["exact", "existence", "absence"] | None
    claim_period: str | None
    freshness_score: Literal[0, 100] | None
    explanation: str
    updated_claim: str | None
    correction_url: str | None
    has_transition: bool
    sources: list[Citation]


class Freshness(BaseModel):
    score: int | None
    current: int
    outdated: int
    scored: int
    unscored_current: int


class Coverage(BaseModel):
    assessed: int
    total: int
    percent: int | None


class Summary(BaseModel):
    verdicts: dict[Verdict, int]
    freshness: Freshness
    evidence_coverage: Coverage


class VerifyResponse(BaseModel):
    project: str
    mode: Literal["live", "example"]
    pipeline: Pipeline
    inference_model: str | None
    checked_at: str
    total_claims: int
    omitted_claims: int
    warnings: list[str]
    summary: Summary
    claims: list[ClaimReport]


class DemoResponse(VerifyResponse):
    answer: str
    scenario: str
