# RevOps Agent Gateway — Monorepo

This is an Agentic GitOps monorepo with two isolated zones:

- **`local-workspace/`** — Employee R&D sandbox. Employees use sparse-checkout to pull only this folder. Contains Python tools, Markdown skills, and context documents created by local AI agents.
- **`remote-gateway/`** — Centralized MCP gateway. Admin-managed. Hosts promoted, QA-approved tools as official MCP endpoints. Never pulled by employees.

## Coding Standards

- Python 3.14+. All functions must have type hints and comprehensive docstrings.
- Docstrings serve double duty: they become MCP tool descriptions when migrated to the gateway.
- No hardcoded API keys or credentials — always use environment variables.
- All data-fetching tools default to **read-only** unless explicit write-permission is granted by an admin.
- Use `ruff` for linting. Line length: 100.

## Architecture

Local agents create tool/skill pairs in `local-workspace/`, auto-push to feature branches, and a GitHub Action QA agent reviews the PR. Admins migrate approved tools into `remote-gateway/core/mcp_server.py` as `@mcp.tool()` decorated functions. Merged skills teach the entire fleet's agents to use the new centralized tools.
