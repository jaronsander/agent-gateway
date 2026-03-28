@AGENTS.md

# Local Workspace

R&D sandbox. Local AI agents connect to data sources, explore workflows, and codify them as skills that get promoted to the shared gateway.

---

## Directory Layout

```
local-workspace/
├── .mcp.json                        ← gateway URL + local MCP connections
├── .env                             ← your API keys (never committed)
├── .env.example                     ← catalog of variable names (committed)
└── .claude/
    ├── rules/                       ← loaded automatically by file type
    │   ├── guardrails.md            ← always: read-only, no hardcoded secrets
    │   ├── skill-standards.md       ← when in .claude/skills/**
    │   ├── python-quality.md        ← when in skills/**/scripts/**/*.py
    │   ├── integration-docs.md      ← when in context/integrations/**
    │   └── session-notes.md         ← when in sessions/**
    ├── agents/                      ← specialized subagents (@-mention or delegate)
    │   ├── qa-pre-check.md          ← reviews skills before push
    │   ├── field-enricher.md        ← enriches API field definitions (has memory)
    │   └── session-scribe.md        ← creates/updates session notes (has memory)
    ├── skills/                      ← slash-commands + promotable tools
    │   ├── integration-onboarding/  ← /integration-onboarding
    │   └── skill-creator/           ← /skill-creator
    ├── output-styles/
    │   └── analyst.md               ← data-focused response style
    └── settings.json                ← permissions + auto-save hook
```

Context and sessions live at the workspace level:
```
local-workspace/
├── context/integrations/<name>/     ← README.md + schema.md per integration
└── sessions/                        ← per-session notes (YYYY-MM-DD-HHmm-slug.md)
```

---

## MCP Configuration

`.mcp.json` has two kinds of entries — both present at the same time:

```json
{
  "mcpServers": {
    "my-gateway": {
      "url": "https://your-gateway.example.com/sse"
    },
    "stripe": {
      "command": "npx",
      "args": ["-y", "@stripe/mcp", "--tools=all"],
      "env": { "STRIPE_API_KEY": "${STRIPE_API_KEY}" }
    }
  }
}
```

**Gateway entry** — always present. All promoted tools live here.
**Local MCP entries** — added per integration during R&D. Remove once the integration is fully promoted and centralized on the gateway.

---

## Available Agents

Use `@agent-name` to invoke directly, or delegate naturally in conversation.

| Agent | When to use |
|---|---|
| `@qa-pre-check` | Before pushing a skill — catches CI failures early |
| `@field-enricher` | After capturing a sample API response — writes business definitions |
| `@session-scribe` | At session start or to log a discovery mid-session |
