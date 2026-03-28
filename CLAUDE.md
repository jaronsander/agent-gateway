# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# RevOps Agent Gateway — Monorepo

Agentic GitOps monorepo with two isolated zones:

- **`local-workspace/`** — Employee R&D sandbox. Employees sparse-checkout only this folder. Local AI agents create Python tools and Markdown skills here.
- **`remote-gateway/`** — Centralized MCP gateway. Admin-managed. Hosts promoted, QA-approved tools as official MCP endpoints. Never pulled by employees.

## Commands

```bash
# Install (from repo root)
pip install -e .
pip install -e ".[dev]"   # includes pytest and ruff

# Lint
ruff check .

# Test
pytest

# Run the remote gateway (stdio transport, default)
python remote-gateway/core/mcp_server.py

# Run as SSE server (for remote deployment)
MCP_TRANSPORT=sse python remote-gateway/core/mcp_server.py

# Run via mcp CLI
mcp run remote-gateway/core/mcp_server.py
```

## Coding Standards

- Python 3.14+. All functions must have type hints and comprehensive docstrings.
- Docstrings serve double duty: they become MCP tool descriptions when migrated to the gateway.
- All credentials via `os.environ` — never hardcoded.
- All data-fetching tools default to **read-only** unless explicit write-permission is granted by an admin.
- `ruff` for linting, line length 100.

## Architecture

### Lifecycle: Local → Gateway

1. **Local agent fetches data** using raw MCP connections (Stripe, Snowflake, CRM, etc.) configured in `local-workspace/.mcp.json`.
2. **Incubation Loop** — if the answer required multi-step logic, the agent codifies it as a Claude Code skill directory at `local-workspace/.claude/skills/<name>/` containing a `SKILL.md` (frontmatter + instructions, becomes a `/slash-command`) and a `scripts/<name>.py` (the Python tool promoted to the gateway).
3. **Auto-push** — agent commits the skill directory to an `employee/<username>` branch and pushes.
4. **CI QA review** — `.github/workflows/qa_agent_review.yml` triggers on PRs touching `local-workspace/.claude/skills/**`. A Claude agent (via OpenRouter, using `remote-gateway/prompts/qa_agent_instructions.md`) reviews for safety, security, type hint coverage, and docstring quality, then posts a structured comment.
5. **Auto-promotion** — on merge, `.github/workflows/auto_promote.yml` injects the script into `remote-gateway/core/mcp_server.py` with `@mcp.tool()`. The docstring becomes the MCP tool description automatically.
6. **Fleet update** — merged skills propagate via `git pull`, teaching all local agents to use the new centralized tool via `/skill-name`.

### Skill/Script Pairing Rule

Every Python script in `local-workspace/.claude/skills/<name>/scripts/` must have a `SKILL.md` sibling in the same skill directory. The skill explains *when* and *why* to invoke the tool; the script is the executable code. This is enforced by the QA agent.

### MCP Server Transports

`remote-gateway/core/mcp_server.py` uses FastMCP and supports two transports:
- **stdio** (default) — local dev and `mcp run`
- **SSE** — remote deployment via `MCP_TRANSPORT=sse`; local agents connect via `<GATEWAY_URL>/sse` in `local-workspace/.mcp.json`

### Session Notes

Local agents maintain per-session notes in `local-workspace/sessions/` using the naming convention `YYYY-MM-DD-<short-topic>.md`. See `local-workspace/CLAUDE.md` for the required structure.

### Zone-Specific Instructions

- `local-workspace/CLAUDE.md` — tool file standards, skill file standards, MCP config details
- `local-workspace/AGENTS.md` — agent identity, tool resolution order, incubation loop, auto-push git protocol, guardrails
- `remote-gateway/CLAUDE.md` — migration workflow, server configuration, admin guardrails
