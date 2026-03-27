@AGENTS.md
# Local Workspace

This is the employee R&D sandbox. Local AI agents operate here to experiment with MCP-connected data sources and codify successful workflows.

## Directory Layout

- **`.claude/skills/<name>/`** — Self-contained Claude Code skills. Each skill is a directory with:
  - `SKILL.md` (required) — YAML frontmatter + instructions. The `name` field becomes `/slash-command`.
  - `scripts/` (optional) — Executable Python/Bash scripts invoked by the skill.
  - `references/` (optional) — Documentation loaded into context as needed.
  - `assets/` (optional) — Templates, icons, or other files used in output.
- **`context/`** — Reference material for agents:
  - **`context/brand/`** — Brand guidelines, templates, tone of voice.
  - **`context/integrations/<name>/`** — Per-integration documentation. Each integration has a `README.md` (business context, capabilities) and `schema.md` (field definitions, enum values, API quirks discovered at runtime). Update these files as you learn new things about an integration — never let schema discoveries live only in a session note.
- **`sessions/`** — Dated session logs. Each agent session creates one file here (see `sessions/README.md` for format). These capture API discoveries, decisions, and open questions that aren't visible in code.

## Skill Standards

Every skill in `.claude/skills/<name>/` must follow this structure:

```
.claude/skills/<name>/
├── SKILL.md           # Required — frontmatter + instructions
├── scripts/           # Executable code (Python, Bash, etc.)
├── references/        # Docs loaded as needed
└── assets/            # Templates, icons, etc.
```

`SKILL.md` frontmatter:
```yaml
---
name: skill-name           # becomes /skill-name slash-command
description: What it does and when to use it.
---
```

Script requirements:
- Type hints on all function signatures.
- Comprehensive docstrings (these become MCP tool descriptions upon promotion to the gateway).
- No hardcoded credentials — use `os.environ` for secrets.
- Default to read-only operations. No mutating calls (POST, DELETE, INSERT, DROP) without explicit approval.
- Reference scripts from SKILL.md using `${CLAUDE_SKILL_DIR}/scripts/<file>.py`.

## MCP Configuration

Local MCP servers are configured in `.mcp.json`. Employees can add their own connections (Stripe, Snowflake, CRM, etc.) for experimentation.
