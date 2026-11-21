"""Conservative verification for a few explicitly stated claim forms."""
import re
from dataclasses import dataclass
from datetime import date
from unicodedata import normalize

if __package__:
    from .claims import LEADING_PERIOD, SENTENCE_BREAK, temporal_hint
else:
    from claims import LEADING_PERIOD, SENTENCE_BREAK, temporal_hint

LIFECYCLE = re.compile(r"^(.{2,80}?) is (?:currently |still )?(?:officially )?supported(?: by (.{2,90}))?$", re.I)
PROVENANCE = re.compile(r"^(.{2,80}?) was (created|invented|founded) by (.{2,100})$", re.I)
DATED_EVENT = re.compile(r"^(.{2,100}?) (was|were) (released|launched|opened|signed|ratified|founded|discovered)(?: (.{2,100}))?$", re.I)
HEDGED = re.compile(r"""\b(?:allegedly|rumou?red|unconfirmed|unverified|could|might|hypothetical|pretend|imagine|ignore|system prompt|reportedly|whether|incorrect|false that|misconception|myth|if|unless)\b|[“”"]""", re.I)
MODEL_INSTRUCTIONS = re.compile(r"\b(?:ignore|override|disregard) (?:all |any |the )?(?:previous|prior|system) instructions\b|\breveal (?:the |your )?system prompt\b", re.I)


@dataclass(frozen=True)
class Proposition:
    kind: str
    subject: str
    predicate: str = ""
    object: str = ""
    maintainer: str = ""


def tidy(text):
    return " ".join(normalize("NFKC", text).translate(str.maketrans("’‘–—", "''--")).split())


def proposition(claim):
    text = tidy(claim.text).rstrip(".")
    if claim.scope == "current" and (match := LIFECYCLE.fullmatch(text)):
        subject, maintainer = match.groups()
        return Proposition("lifecycle", subject, maintainer=maintainer or "")
    if claim.scope == "stable" and (match := PROVENANCE.fullmatch(text)):
        return Proposition("provenance", *match.groups())
    if claim.scope == "historical" and claim.anchored and claim.period:
        text = LEADING_PERIOD.sub("", text)
        text = re.sub(r"\s+(?:yesterday|today|last week|recently)$", "", text, flags=re.I)
        if match := DATED_EVENT.fullmatch(text):
            subject, auxiliary, verb, role = match.groups()
            return Proposition("event", subject, f"{auxiliary} {verb}", role or "")
    return None


def passage_query(claim):
    fact = proposition(claim)
    if fact is None:
        return None
    if fact.kind == "lifecycle":
        return f"{fact.subject} official support status end of life lifecycle {fact.maintainer}".strip()
    if fact.kind == "provenance":
        return f"{fact.subject} {fact.predicate} by {fact.object} official history"
    return f"{fact.subject} {fact.predicate} {fact.object} {claim.period} official record"


def sentences(body):
    for line in body[:80000].splitlines():
        for part in SENTENCE_BREAK.split(tidy(line)):
            if 12 <= len(part) <= 550 and not HEDGED.search(part):
                yield part


def date_in(statement, today):
    simplified = without_ordinals(statement)
    scope, period, _ = temporal_hint(simplified, today)
    if scope in {"historical", "current"} and re.fullmatch(r"\d{4}(?:-\d{2}-\d{2})?", period):
        return period
    return ""


def without_ordinals(statement):
    return re.sub(r"(\d)(?:st|nd|rd|th)\b", r"\1", statement, flags=re.I)


def evidence(url, passage, role, relation, period=""):
    return {
        "url": url, "quote": passage, "summary": passage, "role": role,
        "relation": relation, "period": period, "subject_relation": "same",
        "grounding": "page_passage",
    }


def publisher_matches(body, maintainer):
    if not maintainer:
        return True
    maintainer = re.escape(re.sub(r"^the\s+", "", maintainer, flags=re.I))
    return bool(re.search(rf"(?:copyright|©|maintained by|published by)\s*[^.!?\n]{{0,80}}\b{maintainer}\b", body, re.I))


def lifecycle_proof(fact, body, url, today, quality):
    subject = re.escape(fact.subject)
    intrinsic = quality == "official" and publisher_matches(body, fact.maintainer)
    if not intrinsic and not fact.maintainer:
        return []
    maintainer = re.escape(re.sub(r"^the\s+", "", fact.maintainer, flags=re.I))
    attribution = rf" by (?:the )?{maintainer}" if not intrinsic else ""
    clause_start = r"(?:^|,\s*(?:and\s+)?)"
    no_support = re.compile(rf"{clause_start}{subject} is (?:officially )?no longer (?:officially )?supported{attribution}(?=$|[.,;]|\s+(?:and|as of|since|by)\b)", re.I)
    ended = re.compile(rf"{clause_start}(?:official )?support for {subject} (?:ended|was discontinued|expired)\b", re.I)
    policy = []
    for statement in sentences(body):
        status = no_support.search(statement)
        ended_policy = intrinsic and ended.search(statement)
        if status or ended_policy:
            if temporal_hint(without_ordinals(statement), today)[0] == "future":
                continue
            period = date_in(statement, today)
            if status and not ended_policy and not re.match(r"^as of\b", statement, re.I):
                suffix = statement[status.end():]
                period = date_in(suffix, today) if re.match(r"\s+as of\b", suffix, re.I) else ""
            if period and len(period) == 10:
                event = date.fromisoformat(period)
                if event > today:
                    continue
            if period and len(period) == 4 and int(period) >= today.year:
                continue
            policy.append((statement, period, bool(status)))
    current = next(((statement, period) for statement, period, explicit in policy if explicit and period), None)
    current = current or next(((statement, period) for statement, period, explicit in policy if explicit), None)
    if not current:
        return []
    statement, period = current
    event_periods = {point for _, point, _ in policy if point}
    event_quote, event_period = next(((text, point) for text, point, _ in policy if point), ("", "")) if len(event_periods) == 1 else ("", "")
    rows = [evidence(url, statement, "current", "contradicts", f"since {event_period}" if event_period else period)]
    if event_period:
        rows.extend([
            evidence(url, event_quote, "historical", "supports", f"before {event_period}"),
            evidence(url, event_quote, "change", "context", event_period),
        ])
    return rows


def proof(fact, body, url, today, quality):
    if not isinstance(body, str) or not body.strip() or MODEL_INSTRUCTIONS.search(body):
        return []
    if fact.kind == "lifecycle":
        return lifecycle_proof(fact, body, url, today, quality)
    subject = re.escape(fact.subject)
    if fact.kind == "provenance":
        statement = re.compile(rf"^{subject} was {fact.predicate} by {re.escape(fact.object)}(?=$|[.,;]| and\b)", re.I)
        passage = next((line for line in sentences(body) if statement.search(line)), None)
        return [evidence(url, passage, "current", "supports")] if passage else []
    object_pattern = re.escape(fact.object)
    if fact.object.startswith("from "):
        noun = re.escape(fact.object[5:])
        object_pattern = rf"from (?:(?-i:[A-Z][\w'-]*) ){{0,5}}{noun}"
    suffix = " " + object_pattern if fact.object else ""
    statement = re.compile(rf"^{subject} {re.escape(fact.predicate)}{suffix}(?=$|[.,;]| (?:on|in|at)\b)", re.I)
    for line in sentences(body):
        proposition_text = LEADING_PERIOD.sub("", line)
        if statement.search(proposition_text) and (period := date_in(line, today)):
            return [evidence(url, line, "historical", "supports", period)]
    if fact.predicate == "was released" and fact.object == "from prison":
        return prison_release_proof(subject, body, url, today)
    return []


def prison_release_proof(subject, body, url, today):
    direct = re.compile(rf"^{subject}(?:, [^,]{{8,110}},)? (?:was|is) released from prison\b", re.I)
    antecedent = re.compile(rf"\brelease of {subject}\b", re.I)
    pronoun = re.compile(r"^(?:He|She) was released (?:unconditionally )?on\b.*\b(?:after spending|after serving)\b.*\bin prison\b", re.I)
    for paragraph in body[:80000].splitlines():
        previous = ""
        for sentence in sentences(paragraph):
            period = date_in(sentence, today)
            if period and direct.search(LEADING_PERIOD.sub("", sentence)):
                return [evidence(url, sentence, "historical", "supports", period)]
            if period and antecedent.search(previous) and pronoun.search(sentence):
                passage = f"{previous} {sentence}"
                if passage in tidy(paragraph):
                    return [evidence(url, passage, "historical", "supports", period)]
            previous = sentence
    return []
