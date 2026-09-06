"""Minimal example — set GROQ_API_KEY and run."""

import os
from angvey_lam import Agent, Permission, tool


@tool(description="Echo a message (demo tool)")
def echo(message: str) -> str:
    return f"Echo: {message}"


def main() -> None:
    if not os.getenv("GROQ_API_KEY"):
        print("Set GROQ_API_KEY first.")
        return

    perms = Permission(
        allowed_domains=["arxiv.org", "github.com", "wikipedia.org"],
        allowed_tools=["web_gather", "think", "echo"],
        read_only=True,
        max_steps=8,
    )

    agent = Agent(permissions=perms, tools=[echo])
    result = agent.run(
        "What is agent self-reflection in AI? Give a short accurate summary with sources."
    )
    print("=== Answer ===")
    print(result.answer)
    print("\n=== Steps ===")
    for s in result.steps:
        print(f"  [{s['step']}] {s.get('action')} — {s.get('thought', '')[:80]}")


if __name__ == "__main__":
    main()
