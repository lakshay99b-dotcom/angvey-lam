"""CLI: angvey-lam \"your goal here\" """

from __future__ import annotations

import argparse
import json
import os
import sys

from dotenv import load_dotenv

from .agent import Agent
from .permissions import Permission


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="angvey-lam — controlled language agent")
    parser.add_argument("goal", nargs="?", help="Goal for the agent")
    parser.add_argument("--model", default=os.getenv("ANGVEY_MODEL", "llama-3.3-70b-versatile"))
    parser.add_argument("--domains", default="", help="Comma-separated allowed domains")
    parser.add_argument("--max-steps", type=int, default=10)
    parser.add_argument("--json", action="store_true", help="Print full JSON result")
    args = parser.parse_args()

    if not args.goal:
        print('Usage: angvey-lam "Find recent papers on agent self-reflection"')
        sys.exit(1)

    domains = [d.strip() for d in args.domains.split(",") if d.strip()]
    perms = Permission(
        allowed_domains=domains
        or ["arxiv.org", "github.com", "wikipedia.org", "docs.python.org", "openai.com"],
        max_steps=args.max_steps,
        read_only=True,
    )
    agent = Agent(permissions=perms, model=args.model)
    result = agent.run(args.goal)

    if args.json:
        print(
            json.dumps(
                {
                    "goal": result.goal,
                    "answer": result.answer,
                    "success": result.success,
                    "error": result.error,
                    "steps": result.steps,
                },
                indent=2,
            )
        )
    else:
        print(result.answer)
        if not result.success and result.error:
            print(f"\n[error] {result.error}", file=sys.stderr)


if __name__ == "__main__":
    main()
