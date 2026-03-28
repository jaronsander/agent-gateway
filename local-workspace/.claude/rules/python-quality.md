---
paths:
  - ".claude/skills/**/scripts/**/*.py"
---

# Python Script Quality Standards

These rules apply whenever you are creating or editing Python scripts inside skill `scripts/` directories.

## Type Hints

Required on every function. Parameters and return values both.

```python
# ✅ Correct
def get_revenue(period: str = "30d") -> dict[str, Any]:

# 🛑 Wrong
def get_revenue(period="30d"):
```

## Docstrings

Every function must have a docstring. This is not optional — the docstring becomes the MCP tool description that every operator's AI agent sees when the tool is promoted to the gateway. Write it for a non-technical user, not a developer.

Required format:
```python
def get_revenue(period: str = "30d") -> dict[str, Any]:
    """Fetch total revenue from Stripe for a given time window.

    Args:
        period: Time window (e.g., "7d", "30d", "90d").

    Returns:
        Dict with total_revenue (USD cents), transaction_count, and period.
    """
```

Avoid vague docstrings like "Gets revenue" or "Fetches data." If you can't explain what the output means in one sentence, the docstring isn't complete.

## Credentials

`os.environ` only. Never write a key, token, or password as a string literal.

```python
# ✅ Correct
import os
api_key = os.environ["STRIPE_API_KEY"]

# 🛑 Wrong
api_key = "sk_live_..."
```

## Imports

Use `from __future__ import annotations` at the top. Standard library imports before third-party.

## Python Version

Target Python 3.14+. Use `int | float` union syntax, not `Union[int, float]`.

## Output Design

Scripts should return purposeful data, not raw API responses. Before returning:
- Drop fields the agent doesn't need
- Rename API keys to business-meaningful names where appropriate
- Convert units (e.g., cents → dollars) or resolve enums to human-readable labels
- Flatten nested structures if the nesting adds no value to the agent

The test: can this output go directly into agent context without noise? If the agent would need to filter, convert, or interpret it further, the script hasn't finished its job.

## Linting

Code must pass `ruff check` with line length 100. Run before committing.
