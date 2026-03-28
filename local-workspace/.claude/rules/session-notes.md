---
paths:
  - "sessions/**"
---

# Session Note Standards

These rules apply when creating or editing files in `sessions/`.

## File Naming

```
sessions/YYYY-MM-DD-HHmm-<slug>.md
```

Use today's date, current time (24h), and a 2–4 word slug describing what the session is about. Example: `2026-03-28-1430-stripe-churn-exploration.md`

One file per session. If you open a second Claude Code window on the same day for a different task, create a second file with a different slug.

## Required Sections

```markdown
# Session: <slug>

**Date:** YYYY-MM-DD
**Integration(s):** <comma-separated list>
**Goal:** One sentence — what were we trying to accomplish?

## Discoveries

Log as you go. Each entry: what you found, why it matters.

## Decisions

What did we decide, and why? Include alternatives considered.

## API Quirks

Undocumented behaviors, error messages and their resolutions, pagination gotchas, rate limits hit.

## Open Questions

Things to investigate next session.
```

## What to Log

Log anything that isn't obvious from reading the code or the API docs:
- The actual response shape you got (not what the docs said you'd get)
- Error messages and how you resolved them
- Why you chose one approach over another
- Fields that mean something different than their name suggests

Do not log: what tools you called, what code you wrote, what the user said. Git and the code itself capture those.

## Promote to schema.md

When you log a field discovery here, also update `context/integrations/<name>/schema.md`. Session notes are temporal; schema.md is permanent.
