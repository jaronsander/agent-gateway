---
paths:
  - ".claude/skills/**"
---

# Skill Directory Standards

These rules apply whenever you are creating or editing files inside `.claude/skills/`.

## Required Structure

Every skill directory must have exactly this layout:

```
.claude/skills/<name>/
├── SKILL.md          ← required
└── scripts/
    └── <name>.py     ← required if this skill has a promotable tool
```

Optional: `references/` for docs loaded into context, `assets/` for templates.

## SKILL.md Frontmatter

Every `SKILL.md` must begin with valid YAML frontmatter:

```yaml
---
name: skill-name
description: >
  One or two sentences. What question does this answer? When should Claude
  invoke it? This is what determines auto-invocation — write it precisely.
---
```

The `name` field must be lowercase with hyphens only. It becomes the `/skill-name` slash-command.

The `description` field is used by Claude to decide when to auto-invoke this skill. Write it as a trigger condition, not a summary: "Use when the user asks about Stripe revenue, churn, or MRR" not "A Stripe skill."

## Script Requirements

Scripts in `scripts/` must pass CI QA before promotion. Run `@qa-pre-check` on the skill directory before pushing.

Required:
- Type hints on every function parameter and return value
- Docstring on every function — see Python Quality rules
- `os.environ` for all credentials (never hardcoded)
- Read-only operations only (no POST, DELETE, INSERT, DROP without admin approval)
- Transform, don't pass through — return only the fields downstream agents need, with business-meaningful keys and labels. A script that returns a raw API response unchanged is not ready to promote.

## Naming Convention

Skill directory name: `<integration>-<what>` (e.g., `stripe-revenue`, `hubspot-contacts`)
Script filename: `<integration>_<what>.py` (e.g., `stripe_revenue.py`)
