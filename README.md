# angvey-lam

**Turn any LLM API (Groq recommended) into a controlled Language Agent.**

Add your API key → you get an agent that can:

- Plan and act in a loop
- Use a **smart gatherer** (decision-driven web access — advanced alternative to blind crawling)
- Call only the tools **you** allow
- Treat all web content as **untrusted data** (never as instructions)

Built by **angvey int**. MIT licensed. Open source for transparency.

---

## Quick start

```bash
pip install -e .
export GROQ_API_KEY=gsk_...
angvey-lam "Summarize recent work on AI agent self-reflection"
```

Or in Python:

```python
from angvey_lam import Agent, Permission

perms = Permission(
    allowed_domains=["arxiv.org", "github.com", "wikipedia.org"],
    read_only=True,
    max_steps=10,
)

agent = Agent(permissions=perms)  # uses GROQ_API_KEY
result = agent.run("What is agent self-reflection?")
print(result.answer)
```

Works with any OpenAI-compatible endpoint (set `base_url` + key).

---

## Architecture

User goal → LLM brain (JSON plan) → Agent loop → Permission + SmartGatherer + User tools.

### Smart gatherer (`angvey_gather`)

Inspired by Crawl4AI, redesigned for agents:

| Blind crawl | Smart gather |
|-------------|----------------|
| Fetch whole pages | Decide *where* first |
| Keep everything | Extract only goal-relevant text |
| Fixed depth | Stop when enough signal |
| No permissions | Domain allow/block lists |

---

## Permissions (you stay in control)

```python
Permission(
    allowed_domains=["arxiv.org", "github.com"],
    blocked_domains=["localhost"],
    allowed_tools=["web_gather", "think", "my_tool"],
    read_only=True,
    max_steps=12,
)
```

---

## Safety notes

- Web content is **never** executed as instructions.
- Default is **read-only**.
- Domain and tool allowlists are enforced in code.

## License

MIT © angvey int
