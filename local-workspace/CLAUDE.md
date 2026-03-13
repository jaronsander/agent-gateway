# Local Workspace

This is the employee R&D sandbox. Local AI agents operate here to experiment with MCP-connected data sources and codify successful workflows.

## Directory Layout

- **`tools/`** — Python scripts that perform data extraction, transformation, or analysis. Each file should be a self-contained module with a clearly defined `main()` or primary function.
- **`skills/`** — Markdown SOPs (Standard Operating Procedures) that teach agents when and how to use the corresponding tool. Named to match their tool (e.g., `tools/stripe_churn.py` pairs with `skills/evaluate_churn.md`).
- **`context/`** — Static reference material: brand guidelines, templates, glossaries, personas. Agents read these for domain knowledge.

## Tool File Standards

Every Python tool in `tools/` must follow this structure:

```python
"""
<One-line summary of what this tool does.>

Business Context:
    <Why this tool exists — what business problem it solves.>

Usage:
    <How to invoke this tool, expected inputs/outputs.>
"""

def primary_function(param: str) -> dict:
    """Detailed docstring with args, returns, and raises."""
    ...

if __name__ == "__main__":
    primary_function()
```

Requirements:
- Type hints on all function signatures.
- Comprehensive docstrings (these become MCP tool descriptions upon migration).
- No hardcoded credentials — use `os.environ` for secrets.
- Default to read-only operations. No mutating calls (POST, DELETE, INSERT, DROP) without explicit approval.

## Skill File Standards

Every Markdown skill in `skills/` must include:

1. **Business Problem** — What question or workflow this addresses.
2. **When to Trigger** — The conditions under which an agent should invoke the paired tool.
3. **How to Interpret Output** — Guidance on reading and presenting results to users.
4. **Dependencies** — Which MCP tools or data sources are required.

## MCP Configuration

Local MCP servers are configured in `.mcp.json`. Employees can add their own connections (Stripe, Snowflake, CRM, etc.) for experimentation.
