---
paths:
  - "context/integrations/**"
---

# Integration Documentation Standards

These rules apply whenever you are creating or editing files in `context/integrations/`.

## Required Files Per Integration

```
context/integrations/<name>/
├── README.md    ← business context
└── schema.md    ← field definitions and API quirks
```

Create both files when you first explore a new integration. Never leave an integration directory with only one.

## README.md Contents

Answer these questions:
- What business problems does this integration solve for us?
- What data is available and what isn't?
- What are the known API limitations or quirks we've hit?
- Are there rate limits or pagination behaviors worth knowing?

Keep it short — 20 to 50 lines. This file is loaded as context when the agent uses this integration, so every line needs to earn its place.

## schema.md Contents

For every field the integration returns that we've actually used or cared about:

```markdown
## field_name
- **Display name:** Human-readable label
- **Type:** string | number | currency_usd | percentage | boolean | timestamp | id | array | object
- **Description:** What this field means to the business (not what the API docs say — what WE care about)
- **Notes:** Calculation methodology, caveats, known nulls, enum values
```

## Update Discipline

Update `schema.md` immediately when you confirm a field definition — do not wait until the end of a session. A field discovered but not documented will be re-discovered next session.

When you call `discover_fields()` on the gateway and it returns TODO descriptions, enrich those descriptions here first, then the YAML.
