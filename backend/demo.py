from datetime import date

if __package__:
    from .verifier import build_report
else:
    from verifier import build_report

DEMO_CLAIMS = [
    "Pluto is the ninth planet in the Solar System.",
    "In 2005, Pluto was classified as the ninth planet in the Solar System.",
    "Pluto is a dwarf planet.",
]

NASA = "https://science.nasa.gov/dwarf-planets/pluto/facts/"
IAU_VOTE = "https://www.iau.org/IAU/Iau/News/PR2006/iau-2006-general-assembly-resolution-votes.aspx"
IAU_FAQ = "https://www.iau.org/IAU/IAU/Astronomy-FAQs/FAQs.aspx"

HISTORICAL = {
    "subject_relation": "same",
    "role": "historical",
    "relation": "supports",
    "url": NASA,
    "period": "1930–2006",
    "summary": "NASA records that Pluto was considered the ninth planet from its discovery until its reclassification.",
}
CHANGE = {
    "subject_relation": "same",
    "role": "change",
    "relation": "context",
    "url": IAU_VOTE,
    "period": "2006-08-24",
    "summary": "The IAU adopted a definition of planet that put Pluto in a separate dwarf planet category.",
}
CURRENT = {
    "subject_relation": "same",
    "role": "current",
    "url": IAU_FAQ,
    "period": "2006–present",
    "summary": "The IAU confirms that the 2006 definition still stands and that Pluto is a dwarf planet under it.",
}
DEMO_RESEARCH = {
    "sources": [
        {"title": "Pluto Facts | NASA Science", "url": NASA},
        {"title": "2006 General Assembly results | IAU", "url": IAU_VOTE, "published_date": "2006-08-24"},
        {"title": "Astronomy FAQs | IAU", "url": IAU_FAQ},
    ],
    "content": {
        "assessments": [
            {
                "id": 1,
                "scope": "current",
                "explanation": "Pluto was considered the ninth planet until the IAU changed the classification in 2006. Its current classification is dwarf planet.",
                "updated_claim": "Pluto is a dwarf planet.",
                "correction_url": IAU_FAQ,
                "evidence": [HISTORICAL, CHANGE, {**CURRENT, "relation": "contradicts"}],
            },
            {
                "id": 2,
                "scope": "historical",
                "period": "2005",
                "explanation": "Pluto was still classified as the ninth planet in 2005. The IAU vote that changed its classification came the following year.",
                "evidence": [HISTORICAL, CHANGE],
            },
            {
                "id": 3,
                "scope": "current",
                "explanation": "The IAU classified Pluto as a dwarf planet in 2006 and continues to use that definition.",
                "evidence": [CHANGE, {**CURRENT, "relation": "supports"}],
            },
        ],
    },
}


PYTHON_CLAIMS = [
    "Python 2 receives official bug fixes.",
    "In 2019, Python 2.7 received a bug fix release.",
    "Python was created by Guido van Rossum.",
    "Python was created by James Gosling.",
    "Python will become the only programming language next year.",
]
PYTHON_SUNSET = "https://www.python.org/doc/sunset-python-2/"
PYTHON_2019 = "https://www.python.org/downloads/release/python-2717/"
PYTHON_FAQ = "https://docs.python.org/3/faq/general.html#why-was-python-created-in-the-first-place"
PYTHON_HISTORY = {
    "subject_relation": "same",
    "url": PYTHON_2019, "role": "historical", "relation": "supports", "period": "2019-10-19",
    "summary": "Python.org records Python 2.7.17 as an October 2019 bug fix release for the Python 2.7 line.",
}
PYTHON_CHANGE = {
    "subject_relation": "same",
    "url": PYTHON_SUNSET, "role": "change", "relation": "context", "period": "2020-01-01",
    "summary": "The Python maintainers ended official Python 2 support on January 1, 2020.",
}
PYTHON_AUTHOR = {
    "subject_relation": "same",
    "url": PYTHON_FAQ, "role": "current",
    "summary": "Python’s official FAQ contains Guido van Rossum’s account of starting the language in 1989.",
}
PYTHON_RESEARCH = {
    "sources": [
        {"url": PYTHON_SUNSET, "title": "Sunsetting Python 2 | Python.org"},
        {"url": PYTHON_2019, "title": "Python 2.7.17 release | Python.org"},
        {"url": PYTHON_FAQ, "title": "General Python FAQ | Python documentation"},
    ],
    "content": {
        "assessments": [
            {
                "id": 1,
                "scope": "current",
                "explanation": "Python 2 received official fixes before the January 2020 sunset. The maintainers ended ongoing bug fixes as part of that change.",
                "updated_claim": "Python 2 no longer receives official bug fixes.",
                "correction_url": PYTHON_SUNSET,
                "evidence": [PYTHON_HISTORY, PYTHON_CHANGE, {
                    "url": PYTHON_SUNSET, "role": "current", "relation": "contradicts", "period": "2020–present",
                    "subject_relation": "same",
                    "summary": "The maintainers’ support policy says Python 2 no longer receives official bug fixes after its sunset.",
                }],
            },
            {
                "id": 2, "scope": "historical", "period": "2019",
                "explanation": "Python 2.7.17 was an official bug fix release in October 2019, during the period asserted.",
                "evidence": [PYTHON_HISTORY],
            },
            {
                "id": 3, "scope": "stable",
                "explanation": "The official Python documentation preserves van Rossum’s account of creating Python.",
                "evidence": [{**PYTHON_AUTHOR, "relation": "supports"}],
            },
            {
                "id": 4, "scope": "stable",
                "explanation": "The official record attributes Python’s creation to Guido van Rossum.",
                "evidence": [{**PYTHON_AUTHOR, "relation": "contradicts"}],
            },
            {
                "id": 5, "scope": "future",
                "explanation": "This predicts future adoption. The outcome cannot be established at the time of this example.",
                "evidence": [],
            },
        ],
    },
}

MIXED_CLAIMS = DEMO_CLAIMS[:2] + PYTHON_CLAIMS[2:4]
MIXED_RESEARCH = {
    "sources": DEMO_RESEARCH["sources"] + PYTHON_RESEARCH["sources"][2:3],
    "content": {
        "assessments": (
            DEMO_RESEARCH["content"]["assessments"][:2] + PYTHON_RESEARCH["content"]["assessments"][2:4]
        ),
    },
}

SCENARIOS = {
    "mixed": ("Four claims, four verdicts", MIXED_CLAIMS, MIXED_RESEARCH),
    "pluto": ("Pluto’s reclassification", DEMO_CLAIMS, DEMO_RESEARCH),
    "python": ("Python 2’s support sunset", PYTHON_CLAIMS, PYTHON_RESEARCH),
}


def demo_report(scenario="pluto"):
    title, claims, evidence = SCENARIOS[scenario]
    report = build_report(claims, evidence, date(2026, 11, 21), mode="example", pipeline="recorded")
    return {"answer": "\n".join(claims), "scenario": title, **report}
