from concurrent.futures import ThreadPoolExecutor
from collections import OrderedDict
from datetime import datetime, timezone
from hashlib import sha256
from threading import Lock
from time import monotonic

import httpx

if __package__:
    from .passage_rules import passage_query
else:
    from passage_rules import passage_query

SEARCH_URL = "https://api.tavily.com/search"
_cache = OrderedDict()
_lock = Lock()


class SearchUnavailable(Exception):
    pass


def search(client, query):
    try:
        response = client.post(SEARCH_URL, json={
            "query": query[:400],
            "search_depth": "basic",
            "max_results": 4,
            "include_published_date": True,
            "include_raw_content": "text",
        }, timeout=8)
        response.raise_for_status()
        results = response.json()["results"]
        if not isinstance(results, list):
            raise ValueError("Invalid result list")
        stamp = datetime.now(timezone.utc).isoformat()
        return [
            {**item, "raw_content": (item["raw_content"][:80000] if isinstance(item.get("raw_content"), str) else None),
             "_retrieved_at": stamp}
            for item in results if isinstance(item, dict)
        ]
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
    if query := passage_query(claim):
        return [query]
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


def cached_search(client, namespace, day, scope, query):
    key = (namespace, day, scope, query)
    with _lock:
        cached = _cache.get(key)
        if cached and cached[0] > monotonic():
            _cache.move_to_end(key)
            return [{**item, "_cached": True} for item in cached[1]]
    results = search(client, query)
    lifetime = 600 if scope in {"stable", "historical"} else 120
    if results:
        with _lock:
            _cache[key] = (monotonic() + lifetime, results)
            _cache.move_to_end(key)
            if len(_cache) > 64:
                _cache.popitem(last=False)
    return results


def retrieve(api_key, claims, today):
    tasks = [
        (index, claim.scope, query[:400])
        for index, claim in enumerate(claims, 1)
        for query in queries_for(claim, today)
    ]
    results = {index: [] for index in range(1, len(claims) + 1)}
    errors = []
    namespace = sha256(api_key.encode()).digest()
    with httpx.Client(headers={"Authorization": f"Bearer {api_key}"}, trust_env=False) as client:
        with ThreadPoolExecutor(max_workers=4) as executor:
            pending = {
                (scope, query): executor.submit(cached_search, client, namespace, today, scope, query)
                for scope, query in dict.fromkeys((scope, query) for _, scope, query in tasks)
            }
            for index, scope, query in tasks:
                try:
                    results[index].extend(pending[scope, query].result())
                except SearchUnavailable as error:
                    errors.append(str(error))
    if len(errors) == len(tasks):
        raise SearchUnavailable(errors[0])
    return results, list(dict.fromkeys(errors))
