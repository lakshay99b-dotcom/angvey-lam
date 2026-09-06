"""Permission layer — user decides what the agent may touch."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlparse


@dataclass
class Permission:
    """Explicit allow/deny rules. Default is deny-write."""

    allowed_domains: list[str] = field(default_factory=list)
    blocked_domains: list[str] = field(
        default_factory=lambda: ["localhost", "127.0.0.1", "0.0.0.0"]
    )
    allowed_tools: list[str] = field(default_factory=list)
    read_only: bool = True
    max_steps: int = 12
    max_gather_sources: int = 5
    max_gather_chars: int = 20000

    def domain_allowed(self, url_or_domain: str) -> bool:
        try:
            domain = urlparse(url_or_domain).netloc.lower() or url_or_domain.lower()
        except Exception:
            domain = url_or_domain.lower()
        for b in self.blocked_domains:
            if domain == b or domain.endswith("." + b):
                return False
        if not self.allowed_domains:
            return True
        for a in self.allowed_domains:
            a = a.lower().lstrip(".")
            if domain == a or domain.endswith("." + a):
                return True
        return False

    def tool_allowed(self, name: str, *, is_write: bool = False) -> bool:
        if is_write and self.read_only:
            return False
        if not self.allowed_tools:
            return name in {"web_gather", "think"}
        return name in self.allowed_tools or name in {"web_gather", "think"}
