# Core Guardrails

These rules apply to every session, all files, all actions.

## Read-Only Default

Never call mutating operations against any data source unless the user has explicitly requested a write action and confirmed it in the same session.

Blocked without explicit confirmation: `POST`, `DELETE`, `PUT`, `PATCH`, `INSERT`, `UPDATE`, `DROP`, `TRUNCATE`

If a user asks you to "update a record" or "delete data", pause and confirm the exact mutation before proceeding.

## No Credentials in Code

All API keys, tokens, passwords, and secrets must come from `os.environ`. Never write a credential value into a file. If you see a credential value in user-provided code, flag it immediately and replace it with an `os.environ` reference.

## Gateway First

Before configuring a new local MCP connection, check the gateway with `list_field_integrations()`. If the integration is already promoted, use the gateway's tools instead of setting up a duplicate local connection.

## Session Note Required

If a session involves debugging an integration, discovering undocumented API behavior, creating or modifying a skill, or any decision that isn't obvious from the code — a session note must exist for today in `sessions/`. The PostToolUse hook will remind you if one is missing.
