# Remote Gateway

This is the centralized MCP gateway — admin-managed infrastructure that hosts promoted, QA-approved tools as official MCP endpoints.

## Migration Workflow

When migrating a local tool to the gateway:

1. Copy the function from `local-workspace/tools/<script>.py` into `core/mcp_server.py`.
2. Wrap it with the `@mcp.tool()` decorator. The existing docstring becomes the MCP tool description.
3. Provision required API keys as environment variables in the deployment environment.
4. Merge the corresponding Markdown Skill into `main` so the fleet's local agents learn to use the new centralized tool.

## Guardrails

- **Read-only enforcement.** All newly migrated data-fetching tools must be read-only unless explicit write-permission is structurally required and approved by an admin.
- **No hardcoded secrets.** All credentials come from environment variables (see `.env.example`).
- **Docstring quality matters.** MCP tool descriptions are derived from docstrings — they must be clear, complete, and accurate.

## Server

The MCP server is built with Anthropic's Python MCP SDK (`mcp[cli]`) using the FastMCP pattern, served over stdio transport by default. See `core/mcp_server.py`.
