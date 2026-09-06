"""angvey-gather — production decision-driven web gatherer for AI agents."""

from .gatherer import (
    SmartGatherer,
    GatherResult,
    SourceCandidate,
    ContentBlock,
    arxiv_search,
    wikipedia_search,
    duckduckgo_search,
)
from .extract import (
    extract_relevant,
    html_to_clean_markdown,
    prune_markdown,
    bm25_fit,
    clean_html,
)

__all__ = [
    "SmartGatherer",
    "GatherResult",
    "SourceCandidate",
    "ContentBlock",
    "arxiv_search",
    "wikipedia_search",
    "duckduckgo_search",
    "extract_relevant",
    "html_to_clean_markdown",
    "prune_markdown",
    "bm25_fit",
    "clean_html",
]
