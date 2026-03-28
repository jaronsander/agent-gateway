---
name: integration-onboarding
description: >
  Connect a new data source (MCP server or raw API) to the local workspace.
  Triggers when a user wants to pull data from a new system, when a tool-not-found
  error occurs, or when the user asks about data in an unconnected system.
---

# Integration Onboarding Skill

## Business Problem

When an operator wants to connect a new data source — a third-party MCP server
(Stripe, HubSpot, Postgres) or a raw API — there is a standard sequence that
must be followed to ensure field definitions are registered, the tool is
properly codified, and the gateway can eventually take over the connection.

This skill walks you through that sequence end to end.

---

## When to Trigger

Trigger this skill when:
- A user says "I want to connect [service]" or "can you pull data from [service]?"
- You attempt to call a tool and get a "tool not found" error from the gateway.
- A user asks about data that exists in a system not yet in `.mcp.json`.

---

## Step-by-Step Procedure

### Step 1 — Determine integration type

**MCP server available?** Check if a pre-built MCP package exists:
- Search `npmjs.com` for `@<vendor>/mcp` or `@modelcontextprotocol/server-<vendor>`
- If found → use the MCP path below.
- If not → use the Raw API path below.

---

### Path A — MCP Server

**Step A1 — Confirm credentials**

Identify the required API key or token. Ask the user if they have it.
If not, direct them to the integration's developer portal to generate one.

Once they have it:
1. Ask them to add it to `local-workspace/.env`:
   ```
   STRIPE_API_KEY=sk_test_...
   ```
2. Add the variable name (no value) to `local-workspace/.env.example` under
   the integration's heading so the catalog stays accurate.

**Step A2 — Add to `.mcp.json`**

```json
{
  "mcpServers": {
    "existing-gateway": { "url": "..." },
    "<integration>": {
      "command": "npx",
      "args": ["-y", "@<vendor>/mcp", "--tools=all"],
      "env": { "<API_KEY_VAR>": "${<API_KEY_VAR>}" }
    }
  }
}
```

The `${VAR_NAME}` syntax pulls from the operator's local `.env`. Never paste
a credential value directly into `.mcp.json`.

Restart the MCP client so the new server is discovered.

> `--tools=all` is appropriate for initial exploration — you don't yet know which tools you'll need. As workflows are codified into gateway tools, the local MCP connection becomes redundant and should be retired (see "After Promotion" below).

**Step A3 — Verify connection**

Call any tool from the new MCP server to confirm it connects and returns data.
Capture the raw response — you need it for Step 3.

---

### Path B — Raw API (no MCP package)

**Step B1 — Confirm credentials**

Ask the user for the API key and base URL. Then:
1. Ask them to add credentials to `local-workspace/.env`:
   ```
   INTERNAL_API_KEY=...
   INTERNAL_API_BASE_URL=https://api.example.com
   ```
2. Add the variable names (no values) to `local-workspace/.env.example`.
3. Reference them in your tool script via `os.environ` — never hardcode.

**Step B2 — Write a probe call**

Write a minimal Python snippet in `tools/` that authenticates and fetches one
representative record. Run it via terminal to confirm connectivity and capture
a sample response.

---

### Step 2 — Capture a sample response

You need a real response object — a dict with all the fields the integration
returns — before proceeding. If you have not already, make a test call now and
save the raw output.

---

### Step 3 — Generate field definitions

Invoke `@field-enricher` with the integration name and sample response. It will:
- Fetch the vendor's API documentation for accurate definitions
- Write business-meaningful descriptions to `context/integrations/<integration>/schema.md`
- Create `context/fields/<integration>.yaml` for the gateway field registry

If you prefer to write definitions manually, use the template at `remote-gateway/context/fields/_template.yaml`. Every field needs a real `description` — no TODOs before committing.

---

### Step 4 — Create the skill directory

Create `.claude/skills/<integration>-<what>/` with two files:

**`SKILL.md`** — frontmatter + instructions:
```markdown
---
name: <integration>-<what>
description: >
  One-line description of what this does and when Claude should invoke it.
---

## Business Problem
<what business question this answers>

## When to Trigger
<conditions, keywords, or user intent signals>

## How to Interpret Output
<which fields matter, what thresholds mean>

## Dependencies
- MCP or env vars required: `<VAR_NAME>`
```

**`scripts/<integration>_<what>.py`** — the Python tool:
- Type hints on all functions.
- Comprehensive docstring (becomes the MCP tool description on promotion).
- Credentials via `os.environ` only.
- Read-only by default.
- Transform the output — return only the fields downstream agents need, with business-meaningful keys. The script should replace the raw API in context, not replicate it.

---

### Step 5 — Test and pre-check

Run the script directly:

```bash
python .claude/skills/<integration>-<what>/scripts/<integration>_<what>.py
```

Verify the output matches expectations and the field definitions are complete.

Then invoke `@qa-pre-check` on the skill directory. Fix anything it flags before committing — it's faster than getting a 🛑 from CI after the PR is open.

---

### Step 6 — Commit and push

Stage the skill directory and field definitions, then push to your operator branch:

```bash
BRANCH="operator/$(git config user.name | tr ' ' '-' | tr '[:upper:]' '[:lower:]')"
git checkout "$BRANCH" 2>/dev/null || git checkout -b "$BRANCH"

git add local-workspace/.claude/skills/<integration>-<what>/
git add local-workspace/context/fields/<integration>.yaml

git commit -m "feat(integration): onboard <integration> — <what> tool"
git push origin "$BRANCH"
```

The pipeline takes it from here:
1. A PR to main is opened automatically.
2. The QA agent reviews for safety, security, and quality.
3. On merge, the tool is promoted into the remote gateway and field definitions
   are copied to `remote-gateway/context/fields/`.
4. All agents get the new tool on `git pull`.

**Do not tell the user about the git/PR/merge process unless they ask.**
Just confirm that their question was answered and the workflow has been codified.

---

## How to Interpret Field Discovery Output

After writing the field YAML, verify:
- Every field in your sample response has an entry.
- No `description` reads "TODO" — fill them all before committing.
- `type` is semantically correct, not just the Python type
  (`currency_usd` not `number` for dollar amounts; `timestamp` not `string` for dates).

---

## After Promotion — Retiring the Local Integration

Once the tool has been promoted to the remote gateway (PR merged, gateway redeployed),
the local connection is no longer needed. Retire it:

1. **Remove the MCP entry from `.mcp.json`** (if Path A was used). The gateway now
   handles the integration — keeping the local entry would cause duplicate tool names.

2. **Inform the user:**
   > "[Integration] is now available through the shared gateway. I've removed the
   > local connection — you no longer need to manage credentials for it locally."

3. **The local `.env` entry can stay** — it does no harm and may be useful if the
   operator ever needs to test the integration directly. Do not delete it.

4. **Commit the updated `.mcp.json`** to the operator branch so the change is tracked.

The agent checks for retirement candidates automatically at session start by calling
`list_field_integrations()` on the gateway and comparing against local `.mcp.json` entries.

---

## Dependencies

- Write access to the operator's git branch (automatic via Claude Code).
- MCP server package (if MCP path) or API credentials (if raw API path).
- `ANTHROPIC_API_KEY` set on the gateway server (for the auto-promote CI step).
- `OPENAI_API_KEY` set in GitHub Secrets (for the QA agent CI step).
