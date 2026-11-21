from concurrent.futures import ThreadPoolExecutor

import httpx

SEARCH_URL = "https://api.tavily.com/search"


class SearchUnavailable(Exception):
    pass


def search(client, query):
    try:
        response = client.post(SEARCH_URL, json={
            "query": query[:400],
            "search_depth": "basic",
            "max_results": 4,
            "include_published_date": True,
        }, timeout=8)
        response.raise_for_status()
        results = response.json()["results"]
        if not isinstance(results, list):
            raise ValueError("Invalid result list")
        return [item for item in results if isinstance(item, dict)]
    except httpx.HTTPStatusError as error:
        code = error.response.status_code
        if code in {401, 403}:
            message = "Tavily Search rejected its credentials or access."
        elif code in {429, 432, 433, 434}:
            message = "Tavily Search reached a request or credit limit."
        else:
            message = f"Tavily Search returned HTTP {code}."
        raise SearchUnavailable(message) from None
    except httpx.TimeoutException:
        raise SearchUnavailable("Tavily Search timed out.") from None
    except (httpx.RequestError, ValueError, TypeError, KeyError):
        raise SearchUnavailable("Tavily Search did not return usable results.") from None


def queries_for(claim, today):
    topic = claim.topic or claim.text
    if claim.scope == "historical":
        return [f"Historical record {claim.period} {topic}"]
    if claim.scope == "stable":
        return [f"Authoritative reference {topic}"]
    if claim.scope == "future":
        return [f"Official announcements as of {today.isoformat()} {topic}"]
    return [
        f"Current status official evidence as of {today.isoformat()} {topic}",
        f"History previous status change timeline {claim.text}",
    ]


def retrieve(api_key, claims, today):
    tasks = [
        (index, query)
        for index, claim in enumerate(claims, 1)
        for query in queries_for(claim, today)
    ]
    results = {index: [] for index in range(1, len(claims) + 1)}
    errors = []
    with httpx.Client(headers={"Authorization": f"Bearer {api_key}"}, trust_env=False) as client:
        with ThreadPoolExecutor(max_workers=4) as executor:
            pending = [(index, executor.submit(search, client, query)) for index, query in tasks]
            for index, future in pending:
                try:
                    results[index].extend(future.result())
                except SearchUnavailable as error:
                    errors.append(str(error))
    if len(errors) == len(tasks):
        raise SearchUnavailable(errors[0])
    return results, list(dict.fromkeys(errors))
