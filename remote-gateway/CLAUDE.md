# Remote Gateway

This is the centralized MCP gateway — admin-managed infrastructure that hosts promoted, QA-approved tools as official MCP endpoints. The gateway grows over time as employee R&D is codified and promoted; it becomes the organization's source of truth for shared integrations.

## How the Gateway Relates to Local MCPs

Employees configure their own MCP servers locally (Stripe, HubSpot, Snowflake, etc.) during R&D. That is intentional and required — local connections are the exploration layer. When a workflow is codified and promoted to the gateway, the gateway takes over that integration and the local connection can optionally be retired.

The local workspace always connects to the gateway (for promoted tools) alongside whatever local MCPs the employee is currently working with. Both are in `.mcp.json` at the same time.

## Optional: Proxying Integrations Through the Gateway

For integrations that are fully mature and org-wide, admins can add them to `mcp_connections.json` to proxy them through the gateway server-side. This means:
- The gateway connects to the upstream MCP at startup using server-side env vars
- The tools appear as `<integration>__<tool_name>` on the gateway
- Employees can retire their local connection and use the gateway's copy instead
- Credentials for that integration no longer need to be on employee machines

This is opt-in per integration — not a hard requirement. See `mcp_connections.json` for the format.

## Optional: Access Policy with Claude Code Managed MCP

For organizations that want to govern which MCP servers employees can use, Claude Code supports policy-based control via [`managed-mcp.json`](https://code.claude.com/docs/en/mcp#managed-mcp-configuration). Using Option 2 (allowlist/denylist), admins can define approved MCP servers while still letting employees configure their own within those bounds. This is an IT governance decision and is not required for the gateway to function.

---

## Migration Workflow

**Tool promotion is automated.** When a PR from an `employee/*` branch is merged
into `main`, the `auto_promote.yml` GitHub Action:

1. Calls Claude API to inject new tool functions into `core/mcp_server.py` with
   `@mcp.tool()` and the `validated()` field registry wrapper.
2. Copies field definition YAMLs from `local-workspace/context/fields/` into
   `remote-gateway/context/fields/`.
3. Commits and pushes the result back to `main`.

**Admin responsibilities after auto-promotion:**

1. **Provision API credentials** — add required env vars to the gateway deployment
   environment. The tool will not work until its `os.environ` keys are set.
2. **Redeploy the gateway** — pull the updated `main` and restart the server.
3. **Review the promoted code** — the auto-promote action is AI-driven. Spot-check
   that the function signature, decorator, and `validated()` call are correct.

## Guardrails

- **Read-only enforcement.** All newly migrated data-fetching tools must be read-only unless explicit write-permission is structurally required and approved by an admin.
- **No hardcoded secrets.** All credentials come from environment variables (see `.env.example`).
- **Docstring quality matters.** MCP tool descriptions are derived from docstrings — they must be clear, complete, and accurate.

## Server

The MCP server is built with Anthropic's Python MCP SDK (`mcp[cli]`) using the FastMCP pattern. It supports two transports:

- **stdio** (default) — For local development and `mcp run` usage.
- **SSE** — For remote deployment. Set `MCP_TRANSPORT=sse` to serve over HTTP. Local agents connect via the `/sse` endpoint configured in `local-workspace/.mcp.json`.

See `core/mcp_server.py`.

## Field Registry

Business context definitions for all integration fields live in `context/fields/`.
These are YAML files — one per integration — that map technical field names to
human-readable descriptions, types, and business notes.

### Lifecycle (AI-driven, human-approved)

1. **New integration added** — call `discover_fields(integration, sample_response)` on the
   gateway. It generates a YAML file with inferred types and placeholder descriptions.
2. **Enrich descriptions** — fill in `description` and `notes` for each field in the YAML.
   This can be done by an AI agent given the integration's API documentation.
3. **Validation in production** — every promoted tool wraps its response with
   `validated("integration", result)`. Unknown fields are flagged in the response under
   `_field_validation` without blocking the call.
4. **Periodic drift detection** — call `check_field_drift(integration, fresh_sample)` to
   compare a live response against the registry. Returns `new_fields` and `removed_fields`.
5. **Human review** — a human reviews the drift report and approves YAML updates before merge.

### Adding a New Integration

```python
# On the gateway (via MCP call or admin script):
discover_fields("hubspot", sample_response_dict)
# → creates remote-gateway/context/fields/hubspot.yaml
# → commit the file, redeploy, git pull propagates to local agents
```

### Wrapping a Promoted Tool

```python
@mcp.tool()
def get_contacts(limit: int = 100) -> dict:
    """..."""
    result = _fetch_from_hubspot(limit)
    return validated("hubspot", result)   # field registry check happens here
```

## Gateway Skills

The `skills/` directory contains gateway-focused skills used by admins to design and evolve the central MCP infrastructure.

- **`skills/mcp-builder/`** — The official MCP Builder guide skill ([reference](https://github.com/anthropics/skills/tree/main/skills/mcp-builder)). Use it when creating or refactoring MCP servers and tools that will run in this gateway.
