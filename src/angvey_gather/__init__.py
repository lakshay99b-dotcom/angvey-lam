"""angvey-gather — Decision-driven web gatherer for AI agents.

Inspired by Crawl4AI, but optimized for agents:
- Decide WHERE to look first (search + rank)
- Decide WHAT to extract (goal-aware)
- Stop early when enough signal is collected
- Treat all web content as untrusted data
"""

from .gatherer import SmartGatherer, GatherResult, SourceCandidate
from .extract import extract_relevant, html_to_clean_markdown

__all__ = [
    "SmartGatherer",
    "GatherResult",
    "SourceCandidate",
    "extract_relevant",
    "html_to_clean_markdown",
]
