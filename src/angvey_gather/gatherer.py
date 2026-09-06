"""SmartGatherer — decision-driven alternative to blind crawling."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from urllib.parse import urlparse

import httpx

from .extract import extract_relevant, html_to_clean_markdown


@dataclass
class SourceCandidate:
    url: str
    title: str = ""
    snippet: str = ""
    score: float = 0.0
    domain: str = ""

    def __post_init__(self) -> None:
        if not self.domain:
            try:
                self.domain = urlparse(self.url).netloc.lower()
            except Exception:
                self.domain = ""


@dataclass
class GatherResult:
    goal: str
    sources_used: list[SourceCandidate] = field(default_factory=list)
    content_blocks: list[dict[str, str]] = field(default_factory=list)
    total_chars: int = 0
    stopped_reason: str = "completed"

    def as_context(self) -> str:
        parts = []
        for block in self.content_blocks:
            parts.append(f"### Source: {block.get('url', '')}\n{block.get('text', '')}")
        return "\n\n".join(parts)


SearchFn = Callable[[str, int], list[SourceCandidate]]


def _duckduckgo_html_search(query: str, max_results: int = 8) -> list[SourceCandidate]:
    results: list[SourceCandidate] = []
    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            r = client.get(
                "https://html.duckduckgo.com/html/",
                params={"q": query},
                headers={"User-Agent": "angvey-gather/0.1 (research agent)"},
            )
            r.raise_for_status()
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(r.text, "lxml")
            for a in soup.select("a.result__a")[:max_results]:
                href = a.get("href") or ""
                title = a.get_text(strip=True)
                if not href.startswith("http"):
                    continue
                results.append(SourceCandidate(url=href, title=title, score=1.0))
    except Exception:
        pass
    return results


def _score_candidate(c: SourceCandidate, goal: str) -> float:
    goal_tokens = set(re.findall(r"[a-z0-9]{3,}", goal.lower()))
    text = f"{c.title} {c.snippet}".lower()
    text_tokens = set(re.findall(r"[a-z0-9]{3,}", text))
    overlap = len(goal_tokens & text_tokens)
    boost = 0.0
    for d in ("arxiv.org", "github.com", "wikipedia.org", "docs.", "readthedocs"):
        if d in c.domain:
            boost = 0.3
            break
    return float(overlap) + boost


class SmartGatherer:
    """Permission-aware, goal-driven gatherer."""

    def __init__(
        self,
        *,
        allowed_domains: Optional[list[str]] = None,
        blocked_domains: Optional[list[str]] = None,
        max_sources: int = 5,
        max_chars_total: int = 20000,
        max_chars_per_source: int = 6000,
        search_fn: Optional[SearchFn] = None,
        timeout: float = 20.0,
        user_agent: str = "angvey-gather/0.1 (+https://github.com/lakshay99b-dotcom/angvey-lam)",
    ) -> None:
        self.allowed_domains = [d.lower().lstrip(".") for d in (allowed_domains or [])]
        self.blocked_domains = [d.lower().lstrip(".") for d in (blocked_domains or [])]
        self.max_sources = max_sources
        self.max_chars_total = max_chars_total
        self.max_chars_per_source = max_chars_per_source
        self.search_fn = search_fn or _duckduckgo_html_search
        self.timeout = timeout
        self.user_agent = user_agent

    def _domain_allowed(self, domain: str) -> bool:
        domain = domain.lower()
        for b in self.blocked_domains:
            if domain == b or domain.endswith("." + b):
                return False
        if not self.allowed_domains:
            return True
        for a in self.allowed_domains:
            if domain == a or domain.endswith("." + a):
                return True
        return False

    def search(self, query: str, max_results: int = 10) -> list[SourceCandidate]:
        raw = self.search_fn(query, max_results)
        out = []
        for c in raw:
            if self._domain_allowed(c.domain):
                c.score = _score_candidate(c, query)
                out.append(c)
        out.sort(key=lambda x: -x.score)
        return out

    def fetch_page(self, url: str) -> Optional[str]:
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                r = client.get(url, headers={"User-Agent": self.user_agent})
                r.raise_for_status()
                ctype = r.headers.get("content-type", "")
                if "html" not in ctype and "text" not in ctype:
                    return None
                return r.text
        except Exception:
            return None

    def gather(
        self,
        goal: str,
        *,
        queries: Optional[list[str]] = None,
        seed_urls: Optional[list[str]] = None,
    ) -> GatherResult:
        result = GatherResult(goal=goal)
        candidates: list[SourceCandidate] = []

        if seed_urls:
            for u in seed_urls:
                c = SourceCandidate(url=u)
                if self._domain_allowed(c.domain):
                    candidates.append(c)

        search_queries = queries or [goal]
        for q in search_queries:
            candidates.extend(self.search(q, max_results=8))

        seen = set()
        unique: list[SourceCandidate] = []
        for c in candidates:
            key = hashlib.sha1(c.url.encode()).hexdigest()
            if key in seen:
                continue
            seen.add(key)
            unique.append(c)

        unique.sort(key=lambda x: -x.score)
        unique = unique[: self.max_sources * 2]

        total = 0
        for c in unique:
            if len(result.sources_used) >= self.max_sources:
                result.stopped_reason = "max_sources"
                break
            if total >= self.max_chars_total:
                result.stopped_reason = "max_chars"
                break

            html = self.fetch_page(c.url)
            if not html:
                continue

            md = html_to_clean_markdown(html, base_url=c.url)
            relevant = extract_relevant(md, goal, max_chars=self.max_chars_per_source)
            if len(relevant) < 80:
                continue

            result.sources_used.append(c)
            result.content_blocks.append({"url": c.url, "title": c.title, "text": relevant})
            total += len(relevant)

        result.total_chars = total
        if not result.content_blocks:
            result.stopped_reason = "no_content"
        return result
