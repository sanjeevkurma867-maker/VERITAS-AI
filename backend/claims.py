import re
from dataclasses import dataclass
from datetime import date, timedelta

SCOPES = ("current", "historical", "stable", "future", "unclear")
MAX_CLAIMS = 5
MAX_ANSWER_LENGTH = 6000

SENTENCE_BREAK = re.compile(
    r"(?<!\b[A-Z]\.)(?<!\b(?:Dr|Mr|Ms|St)\.)(?<!\b(?:Mrs|Inc|Ltd)\.)(?<=[.!?])\s+|;\s*"
)
BULLET = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+")
JOIN = re.compile(r",?\s+\b(and|but|whereas|while)\b\s+", re.IGNORECASE)
VERB = re.compile(
    r"\b(?:is|are|was|were|has|have|had|can|will|became|remains?|changed|"
    r"announced|launched|released|ended|began|includes|receives|supports|"
    r"runs|uses|leads|contains|operates|served|orbited|orbits|landed|rotates|died|won)\b",
    re.IGNORECASE,
)
MONTH_NAMES = "January February March April May June July August September October November December".split()
MONTH_NUMBERS = {name[:3].lower(): number for number, name in enumerate(MONTH_NAMES, 1)}
MONTH_PATTERN = "|".join(name[:3] + (f"(?:{name[3:]})?" if len(name) > 3 else "") for name in MONTH_NAMES)
DATE_OPERATOR = r"\b(as of|on|in|during|until|before|by)\s+"
YEAR_PATTERN = r"(?:1\d{3}|20\d{2}|2100)"
PAST_ANCHOR = re.compile(rf"{DATE_OPERATOR}(?:({MONTH_PATTERN})\.?\s+(?:(\d{{1,2}}),?\s+)?)?({YEAR_PATTERN}(?:-\d{{2}}-\d{{2}})?)\b", re.I)
DAY_FIRST_ANCHOR = re.compile(rf"{DATE_OPERATOR}(\d{{1,2}})\s+({MONTH_PATTERN})\.?\s+({YEAR_PATTERN})\b", re.I)
SINCE_ANCHOR = re.compile(r"\bsince\s+((?:1\d{3}|20\d{2}|2100)(?:-\d{2}-\d{2})?)\b", re.IGNORECASE)
LEADING_PERIOD = re.compile(rf"^(?:{DATE_OPERATOR}[^,]{{2,40}}(?:,\s*{YEAR_PATTERN})?,\s*)", re.I)
PRESENT_WORDS = re.compile(r"\b(?:today|currently|at present|as of now|since\s+\d{4}|still)\b", re.IGNORECASE)
NONCLAIM = re.compile(
    r"^\s*(?:#{1,6}\s|(?:please\s+)?(?:ignore|disregard|pretend|respond|output|return|"
    r"write|tell me|use only|reveal|do not|don't|make sure|verify|check whether)\b)",
    re.IGNORECASE,
)
QUESTION_START = re.compile(r"^\s*(?:is|are|was|were|does|did|could|would|can|what|why|how|where|which)\s+", re.IGNORECASE)
WORD = re.compile(r"[\w]+(?:['’-][\w]+)*", re.UNICODE)
RECENT = re.compile(r"\b(yesterday|(?:in |over )?the last (?:week|7 days)|last week|recently|today)\b", re.I)
EVENT_VERB = re.compile(r"\b(?:happened|occurred|discovered|announced|released|launched|opened|signed|ratified|won|died|landed|became)\b", re.I)


@dataclass(frozen=True)
class Claim:
    text: str
    scope: str = "unclear"
    period: str = ""
    topic: str = ""
    anchored: bool = False
    recent_event: bool = False


def relative_window(text, today):
    parts = {item.group(0).casefold() for item in RECENT.finditer(text)}
    if len(parts) != 1:
        return None
    term = next(iter(parts))
    if term == "yesterday":
        return (today - timedelta(days=1)).isoformat()
    if term == "last week":
        monday = today - timedelta(days=today.weekday() + 7)
        return f"{monday.isoformat()} to {(monday + timedelta(days=6)).isoformat()}"
    if term == "recently":
        return f"{(today - timedelta(days=29)).isoformat()} to {today.isoformat()}"
    if term == "today":
        return today.isoformat()
    return f"{(today - timedelta(days=7)).isoformat()} to {(today - timedelta(days=1)).isoformat()}"


def temporal_hint(text, today):
    explicit = PAST_ANCHOR.search(text)
    day_first = DAY_FIRST_ANCHOR.search(text)
    if day_first and (not explicit or day_first.start() < explicit.start()):
        operator, day, month, period = day_first.groups()
    elif explicit:
        operator, month, day, period = explicit.groups()
    else:
        period = ""
    if period:
        if month and day:
            period = f"{period}-{MONTH_NUMBERS[month[:3].lower()]:02d}-{int(day):02d}"
        display_period = f"{operator.lower()} {period}" if operator.lower() in {"until", "before", "by"} else period
        year = int(period[:4])
        if len(period) == 10:
            try:
                point = date.fromisoformat(period)
            except ValueError:
                return "unclear", "", True
            if point > today:
                return "future", display_period, True
            if point == today:
                return "current", display_period, True
            return "historical", display_period, True
        if year < today.year:
            return "historical", display_period, True
        if year > today.year:
            return "future", display_period, True
        return "unclear", display_period, False
    if re.search(r"\blast year\b", text, re.IGNORECASE):
        return "historical", str(today.year - 1), True
    if re.search(r"\b(?:next year|next month|next week|will be|will become)\b", text, re.IGNORECASE):
        return "future", "", True
    window = relative_window(text, today)
    if window and (window != today.isoformat() or EVENT_VERB.search(text)):
        if " to " in window and not EVENT_VERB.search(text):
            return "unclear", window, True
        return "historical", window, True
    since = SINCE_ANCHOR.search(text)
    if since:
        return "current", f"since {since[1]}", True
    if PRESENT_WORDS.search(text):
        return "current", "", True
    if re.search(r"\b(?:previously|formerly|used to|was once|last month|last week)\b", text, re.IGNORECASE):
        return "historical", "", True
    if re.search(r"\b(?:was|were) (?:created|invented|founded|born)\b", text, re.IGNORECASE):
        return "stable", "", False
    if re.search(r"\b(?:was|were|had|became|served|landed)\b", text, re.IGNORECASE):
        return "historical", "", False
    if VERB.search(text):
        return "current", "", False
    return "unclear", "", False


def split_compound(text):
    remainder = text
    pieces = []
    while True:
        for separator in JOIN.finditer(remainder):
            left = remainder[:separator.start()].strip()
            right = remainder[separator.end():].strip()
            prefix = LEADING_PERIOD.match(left)
            proposition = left[prefix.end():] if prefix else left
            left_verb, right_verb = VERB.search(proposition), VERB.search(right)
            if not left_verb or not right_verb or not left_verb.start():
                continue

            subject = proposition[:left_verb.start()].strip()
            if not right_verb.start():
                if len(WORD.findall(subject)) > 9:
                    continue
                right = f"{subject} {right}"
            if prefix and separator[1].lower() == "and" and not (PRESENT_WORDS.search(right) or PAST_ANCHOR.search(right)):
                right = prefix[0] + right
            pieces.append(left.rstrip(",") + ".")
            remainder = right
            break
        else:
            return [*pieces, remainder]


def make_claim(text, today, *, scope="unclear", period="", topic=""):
    hint, hinted_period, anchored = temporal_hint(text, today)
    return Claim(
        text=text,
        scope=hint if anchored or scope == "unclear" else scope,
        period=hinted_period or period,
        topic=topic,
        anchored=anchored,
        recent_event=bool(hint == "historical" and EVENT_VERB.search(text) and relative_window(text, today) == hinted_period),
    )


def extract_candidates(text, today):
    result = {}
    for line in text.splitlines():
        line = BULLET.sub("", line.strip())
        for part in SENTENCE_BREAK.split(line):
            part = " ".join(part.split()).strip()
            if part.rstrip("\"'”’").endswith(("?", ":")) or NONCLAIM.match(part) or QUESTION_START.match(part):
                continue
            for candidate in split_compound(part):
                if len(WORD.findall(candidate)) < 3:
                    continue
                if candidate.rstrip("\"'”’").endswith("?") or NONCLAIM.match(candidate):
                    continue
                key = candidate.casefold().rstrip(".!?")
                result.setdefault(key, make_claim(candidate, today))
    return list(result.values())
