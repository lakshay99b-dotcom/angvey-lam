"""Clean extraction utilities — HTML → agent-ready text."""

from __future__ import annotations

import re
from typing import Optional

from bs4 import BeautifulSoup
import html2text


def html_to_clean_markdown(html: str, base_url: Optional[str] = None) -> str:
    """Convert raw HTML to clean, LLM-friendly markdown."""
    soup = BeautifulSoup(html, "lxml")

    for tag in soup(["script", "style", "noscript", "iframe", "svg", "canvas"]):
        tag.decompose()

    for selector in [
        "nav", "footer", "header", "aside",
        "[role=navigation]", "[role=banner]", "[role=contentinfo]",
        ".nav", ".navbar", ".footer", ".sidebar", ".advertisement",
        ".cookie", ".popup", ".modal", "#cookie",
    ]:
        for el in soup.select(selector):
            el.decompose()

    main = soup.find("main") or soup.find("article") or soup.find(attrs={"role": "main"})
    root = main if main else soup.body or soup

    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = True
    converter.ignore_emphasis = False
    converter.body_width = 0
    converter.skip_internal_links = True
    if base_url:
        converter.baseurl = base_url

    md = converter.handle(str(root))
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    return md


def extract_relevant(
    markdown: str,
    goal: str,
    max_chars: int = 6000,
) -> str:
    """Heuristic relevance trim for agents."""
    if not markdown or not goal:
        return (markdown or "")[:max_chars]

    goal_tokens = set(re.findall(r"[a-z0-9]{3,}", goal.lower()))
    if not goal_tokens:
        return markdown[:max_chars]

    paragraphs = re.split(r"\n\s*\n", markdown)
    scored = []
    for i, p in enumerate(paragraphs):
        p_tokens = set(re.findall(r"[a-z0-9]{3,}", p.lower()))
        overlap = len(goal_tokens & p_tokens)
        scored.append((overlap, i, p))

    scored.sort(key=lambda x: (-x[0], x[1]))
    selected_idx = set()
    total = 0
    for score, i, p in scored:
        if score == 0 and total > 0:
            break
        if total + len(p) > max_chars and total > 0:
            break
        selected_idx.add(i)
        if i > 0:
            selected_idx.add(i - 1)
        if i + 1 < len(paragraphs):
            selected_idx.add(i + 1)
        total += len(p)
        if total >= max_chars:
            break

    if not selected_idx:
        return markdown[:max_chars]

    ordered = [paragraphs[i] for i in sorted(selected_idx)]
    out = "\n\n".join(ordered)
    return out[:max_chars]
