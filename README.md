# Agent Gateway

> Distributed agent work. Governed through middleware. One source of truth.

As AI agents proliferate across a business, three problems compound fast: agents waste tokens on raw, unrefined context; every team re-solves the same problems independently; and the same data fields get interpreted differently by different agents and teams.

Agent Gateway is a GitOps monorepo that addresses all three. Employees explore data and workflows in personal sandboxes. Valuable work gets codified into tools and promoted to a shared gateway — a governed MCP server that accumulates the organization's business context: what tools exist, what each field means in your business, and how processes work. Every agent that connects to the gateway inherits that context instead of rebuilding it from scratch.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Three Pillars

### 1. Context efficiency through progressive codification

Early in an integration's life, agents spend tokens on exploration: raw API calls, large data payloads, reflection, planning. This is expected and necessary. The goal is to not stay there.

As an agent answers the same class of question repeatedly, it codifies the workflow: the API calls become a Python script that fetches and transforms data into a clean, purposeful shape. That script becomes a gateway tool. Future agents call the tool instead of the raw API — they receive exactly the fields they need, pre-labeled with business meaning, and nothing else.

Over time, the cost per task falls. Context gets smaller and more precise. The tokens that used to go toward wrestling with raw data go toward the actual work.

This is the core mechanic: **exploration → codification → refinement**. Every promoted tool is the organization learning something.

### 2. Distributed agent work across teams

Employees work independently in local sandboxes — no central bottleneck for exploration. Each employee's agent connects directly to the data sources they need and works freely. When a workflow proves valuable and repeatable, it flows upward through a pull request into the shared gateway, where it becomes available to every other agent in the org.

The result is a distributed contribution model: many agents explore in parallel, the best work rises to shared infrastructure, and no single team carries the burden of building everything.

> **Roadmap:** As teams and permission needs grow, access to gateway tools will be scopeable via per-team MCP keys. This is not implemented today but is a natural next step as the org grows.

### 3. Governance and safety through middleware

The gateway is not a direct API passthrough — it is middleware. Every promoted tool is QA-reviewed before merge, wrapped with a field validation layer on the gateway, and read-only by default. Mutating operations require explicit admin sign-off in the code review.

The single mandatory human gate is the merge decision. Everything else — PR creation, QA review, tool injection, field registry updates — is automated. The admin reads a QA comment and decides. That's it.

This model scales: a governance layer that requires no ongoing maintenance burden and applies uniformly to every tool, from every team, for every agent that connects.

---

## The Source of Truth

The gateway's most important long-term output is not the tools — it's the context those tools carry.

Every promoted tool wraps its response with a field validation layer. Field definitions live in `remote-gateway/context/fields/<integration>.yaml` and describe each data field not just technically (type, nullable) but semantically: what does `amount` mean in Stripe in your business? What does `stage` mean in your HubSpot pipeline? What does `arr` mean in your data warehouse, and how does your org calculate it?

These definitions are written once, validated continuously, and shared with every agent that connects to the gateway. As more agents are layered onto the business — for analytics, operations, customer support, finance — they all inherit the same vocabulary. Nobody reinterprets the same field independently. Nobody builds on a stale definition.

The gateway becomes the place the business goes to understand what its data means.

---

## Two Perspectives

### What an employee experiences

```
You ask your AI agent a question about revenue
        │
        ▼
Agent calls Stripe MCP locally → fetches raw data → answers you
        │
        ▼  (if the query was complex, multi-step, or likely to recur)
Agent creates a skill in .claude/skills/stripe-revenue/
  └── SKILL.md         ← when/why to use this; becomes /stripe-revenue slash-command
  └── scripts/get.py   ← Python logic that fetches + transforms data for clean context
        │
        ▼
Agent tells you: "Codified into /stripe-revenue and pushed for review."
        │
        ▼  (background — you don't do anything)
PR opens → QA agent reviews → structured comment posted on the PR
        │
        ▼  (human: admin reads QA comment and merges)
        │
        ▼  (background — you don't do anything)
Tool promoted to shared gateway → field definitions copied → all agents learn it
        │
        ▼
You git pull → /stripe-revenue is now a shared slash-command for everyone
               Next time someone asks about revenue, they skip the raw API entirely
```

### What happens automatically (no human needed)

| Event | Automation |
|---|---|
| Agent writes a file | Hook checks that a session note exists for today |
| Agent finishes a response | Hook commits and pushes `local-workspace/` to `employee/<username>` branch |
| Push to `employee/*` with new skills | `auto_pr.yml` opens a PR to main |
| PR opened or updated | `qa_agent_review.yml` runs QA agent, posts review comment on the PR |
| PR merged to main from `employee/*` | `auto_promote.yml` injects tool into `remote-gateway/core/mcp_server.py` with `@mcp.tool()` and field validation wrapper; copies field definitions; commits back to main |

### What requires human input

| Step | Who | What |
|---|---|---|
| Initial repo setup | Admin | Deploy gateway, add `OPENROUTER_API_KEY` to GitHub Secrets |
| Employee onboarding | Employee | Sparse checkout, add credential to `.env`, add MCP to `.mcp.json` |
| Connecting a new local MCP | Employee | Add entry to `.mcp.json` with local API key |
| Merging a PR | Admin | Read QA comment, decide to approve and merge |
| Provisioning env vars after promotion | Admin | Set new env vars on the gateway server, redeploy |
| (Optional) Centralizing an integration | Admin | Add to `mcp_connections.json`, set server env vars, redeploy |

---

## Repository Structure

```
agent-gateway/
│
├── local-workspace/              ← employees sparse-checkout only this
│   ├── .mcp.json                 ← gateway URL + personal local MCPs
│   ├── .env.example              ← credential catalog (copy to .env, never commit .env)
│   └── .claude/
│       ├── CLAUDE.md             ← workspace instructions (loaded every session)
│       ├── AGENTS.md             ← agent directives: incubation loop, git protocol
│       ├── settings.json         ← permissions + hooks (session note check, auto-push)
│       └── skills/
│           ├── integration-onboarding/   ← /integration-onboarding slash-command
│           ├── skill-creator/            ← /skill-creator slash-command
│           └── <name>/                   ← skills created during R&D
│               ├── SKILL.md              ← frontmatter + instructions
│               └── scripts/
│                   └── <name>.py         ← Python tool (promoted to gateway on merge)
│
├── remote-gateway/               ← admin-managed, never pulled by employees
│   ├── core/
│   │   ├── mcp_server.py         ← FastMCP gateway server
│   │   ├── field_registry.py     ← field definition loader and drift detector
│   │   └── mcp_proxy.py          ← optional: proxies upstream MCPs server-side
│   ├── context/
│   │   └── fields/               ← per-integration field definition YAMLs (the source of truth)
│   ├── mcp_connections.json      ← optional: upstream MCPs to proxy through gateway
│   └── prompts/
│       └── qa_agent_instructions.md
│
├── .github/
│   ├── workflows/
│   │   ├── auto_pr.yml           ← opens PRs when employee/* branch gets new skills
│   │   ├── qa_agent_review.yml   ← QA agent reviews every tool PR
│   │   └── auto_promote.yml      ← promotes merged tools into the gateway
│   └── scripts/
│       └── promote_tools.py      ← AI-powered tool injection script
│
├── copier.yml                    ← template config (for copier users)
└── pyproject.toml
```

---

## Setup (Admin, One-Time)

### 1. Create your repo

**Option A — GitHub Template (quickest)**
Click **"Use this template"** at the top of this page.

**Option B — copier (best for agencies managing multiple clients)**
```bash
pip install copier
copier copy gh:your-org/agent-gateway ./my-gateway
```

Copier prompts for: `project_name`, `project_slug`, `gateway_url`, `github_org`.

### 2. Deploy the remote gateway

```bash
pip install -e .

# Set required env var
export MCP_SERVER_NAME=my-org-gateway

# Run locally for testing (stdio)
python remote-gateway/core/mcp_server.py

# Run for remote access (SSE — what employees connect to)
MCP_TRANSPORT=sse python remote-gateway/core/mcp_server.py
```

Deploy target: any Python host — Railway, Fly.io, VPS, Docker. The SSE endpoint is `https://your-domain.com/sse`.

### 3. Configure GitHub Secrets

In your repo settings → Secrets and variables → Actions, add:

| Secret | Used by |
|---|---|
| `OPENROUTER_API_KEY` | QA agent review + auto-promotion |

### 4. Set the gateway URL in the repo

Edit `local-workspace/.mcp.json` and replace `[[ gateway_url ]]` with your SSE endpoint.

---

## Employee Onboarding (Per Person)

Employees only pull `local-workspace/` — they never see gateway code or admin credentials.

### Sparse checkout

```bash
git clone --no-checkout https://github.com/YOUR_ORG/YOUR_REPO.git
cd YOUR_REPO
git sparse-checkout init --cone
git sparse-checkout set local-workspace
git checkout main
```

### Add credentials for local R&D

```bash
cp local-workspace/.env.example local-workspace/.env
# Edit .env — add your API keys for the integrations you'll explore
```

### Connect local MCP servers

Edit `local-workspace/.mcp.json` to add the integrations you need locally:

```json
{
  "mcpServers": {
    "my-gateway": { "url": "https://gateway.example.com/sse" },
    "stripe": {
      "command": "npx",
      "args": ["-y", "@stripe/mcp", "--tools=all"],
      "env": { "STRIPE_API_KEY": "${STRIPE_API_KEY}" }
    }
  }
}
```

The `${STRIPE_API_KEY}` reference reads from your `.env` file. The gateway entry gives you access to all previously promoted tools.

> **Context note:** `--tools=all` is appropriate for early exploration — you don't yet know which tools you'll need. As integrations mature and core workflows are codified into gateway tools, narrow or remove the local MCP connection. The goal over time is to replace broad raw-API access with targeted gateway tools that return clean, pre-labeled data.

### Open Claude Code

Open the `local-workspace/` directory in Claude Code. The skills, hooks, and MCP config load automatically.

---

## Day-to-Day Usage

### Asking questions

Just ask. The agent calls whatever MCP tools are available — local or gateway — and answers. If the question is simple, that's the end of it.

### When the agent codifies something

If a question required multiple steps, the agent creates a skill directory and tells you:

> "Codified into `/stripe-revenue` and pushed for review."

A PR will appear in the repo within seconds. You don't need to do anything.

### Connecting a new integration

Use `/integration-onboarding`. It walks through finding the MCP package, adding credentials to `.env`, adding the entry to `.mcp.json`, capturing a sample response, and creating the field definitions.

### Checking what's available

- **Local MCPs:** `list_tools` from your MCP client shows everything connected.
- **Gateway tools:** Call `health_check()` and `list_field_integrations()` on the gateway.
- **Field definitions:** Call `lookup_field("stripe", "amount")` to see what a field means in your business context.
- **Your skills:** Type `/` in Claude Code to see all available slash-commands.

### After a PR is merged

```bash
git pull
```

New skills are immediately available as slash-commands. New promoted tools are available through the gateway.

---

## The Full Lifecycle

### Stage 1 — Local exploration

Employee works in `local-workspace/`. Agent uses local MCPs (direct API connections). This is the expensive phase: raw data in context, multiple tool calls, exploration of what fields and endpoints exist. Session notes capture discoveries. Nothing is shared yet — this is pure R&D.

**Human action:** Configure `.mcp.json`, add credentials to `.env`.

### Stage 2 — Codification

When a workflow proves valuable and repeatable, the agent creates a skill directory in `.claude/skills/<name>/`:
- `SKILL.md` — when/why to use this, how to interpret output. Becomes a `/name` slash-command.
- `scripts/<name>.py` — the Python logic. The script fetches data and transforms it into a purposeful shape — returning only what downstream agents need, labeled with business meaning. Type hints and docstring are required (the docstring becomes the MCP tool description after promotion).

The agent also updates `context/integrations/<name>/schema.md` with field definitions discovered during exploration.

**Human action:** None. The agent does this.

### Stage 3 — Auto-push

The Stop hook in `settings.json` automatically commits `local-workspace/` and pushes to the employee's `employee/<username>` branch after each response. A milestone push with a meaningful commit message happens when the skill is complete.

**Human action:** None. The hook runs automatically.

### Stage 4 — Auto-PR

When the push lands on an `employee/*` branch with new skill files, `auto_pr.yml` opens a pull request to `main` within seconds. The PR description lists the new tools and explains what will happen on merge.

**Human action:** None. GitHub Actions creates the PR.

### Stage 5 — QA review

`qa_agent_review.yml` runs a Claude agent (via OpenRouter) that reviews the PR diff for:
- **Safety** — no mutating operations (POST, DELETE, INSERT, DROP, PUT, PATCH)
- **Security** — no hardcoded API keys or credentials
- **Quality** — type hints present, docstring complete and clear
- **Pairing** — every script has a `SKILL.md` in the same directory

The agent posts a structured comment: either `🛑 QA FAILED` with the exact violation, or `✅ Passed Automated QA` with a migration summary for the admin.

**Human action:** None. The review is automatic.

### Stage 6 — Human merge decision

An admin reads the QA comment and decides whether to merge. This is the only mandatory human gate in the pipeline. The QA comment gives everything needed to make the decision.

**Human action:** Admin reviews and merges (or requests changes).

### Stage 7 — Auto-promotion

On merge from an `employee/*` branch, `auto_promote.yml`:
1. Calls Claude (via OpenRouter) to inject the Python function into `remote-gateway/core/mcp_server.py` with `@mcp.tool()` decorator and field validation wrapper.
2. Copies `context/fields/*.yaml` files to `remote-gateway/context/fields/`.
3. Commits and pushes the updated gateway back to `main`.
4. Prints a list of env vars the new tool requires (for admin to provision).

**Human action:** None during promotion. After it completes, admin must provision the listed env vars on the gateway server and redeploy.

### Stage 8 — Gateway active

After the admin redeploys the gateway, the new tool is live. Every employee's agent can now call it — and receives pre-transformed, business-labeled data instead of raw API responses.

**Human action:** Admin provisions env vars + redeploys.

### Stage 9 — Fleet sync

Employees run `git pull`. The new `SKILL.md` is pulled into their workspace — the `/tool-name` slash-command is immediately available. Their agent can now route queries to the centralized gateway tool instead of the local MCP.

**Human action:** Employee runs `git pull`.

### Stage 10 — Retire local connection

Once the gateway carries a promoted tool for an integration, the local MCP connection becomes redundant for that workflow. The employee removes that entry from `.mcp.json`. The gateway version uses server-side credentials and returns clean data — the employee no longer needs a local API key or raw tool access.

Over time, this is how context gets smaller: each promoted tool replaces a broad local connection with a targeted, purposeful one.

**Human action:** Employee cleans up `.mcp.json`.

---

## The Field Registry: Building the Business Semantic Layer

Every promoted tool wraps its response with `validated("integration", result)`. Field definitions live in `context/fields/<integration>.yaml` and are the organization's semantic layer — not just schemas, but meaning:

- What does `amount` mean in Stripe? Net, gross, before or after fees?
- What does `stage` mean in HubSpot? How does your sales team define each value?
- What does `arr` mean in your data warehouse? How is it calculated, and who owns the definition?

These answers are written once during integration onboarding, refined as the business evolves, and shared with every agent that connects to the gateway. The field registry tools make definitions queryable:

```python
# Via MCP call to the gateway:
lookup_field("stripe", "amount")           # → definition, type, business notes
get_field_definitions("hubspot")           # → full schema for the integration
check_field_drift("stripe", fresh_sample)  # → new_fields, removed_fields, unchanged
```

As more agents are layered onto the business — for analytics, operations, finance, customer support — they all inherit the same vocabulary. Nobody reinterprets the same field independently. Nobody builds on a stale definition.

---

## Optional: Centralizing an Integration on the Gateway

Once an integration is mature and used org-wide, an admin can move its credentials server-side so employees no longer need local API keys for it.

Edit `remote-gateway/mcp_connections.json`:

```json
{
  "connections": {
    "stripe": {
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@stripe/mcp", "--tools=all"],
      "env": { "STRIPE_API_KEY": "${STRIPE_API_KEY}" }
    }
  }
}
```

Set `STRIPE_API_KEY` on the gateway server, redeploy. The gateway now proxies all of Stripe's tools as `stripe__<tool_name>`. Employees remove their local Stripe MCP entry — the gateway handles it.

> **Note:** Centralizing the raw MCP gives every employee access to all Stripe tools through the gateway. This is useful before custom tools exist. As integrations mature, the goal is to replace raw tool access with promoted, purpose-built tools that return clean data — so the raw proxy becomes less necessary over time.

---

## Optional: Access Policy

For organizations that need governance over which MCP servers employees can configure, Claude Code supports a policy-based allowlist/denylist via [`managed-mcp.json`](https://code.claude.com/docs/en/mcp#managed-mcp-configuration) deployed at the OS level. This is an IT decision and is not required for the gateway to function.

---

## Coding Standards

- **Python 3.14+.** Type hints on every function parameter and return value.
- **Docstrings are MCP descriptions.** Write them to be clear to non-technical users — they appear as tool descriptions in every AI agent connected to the gateway.
- **No hardcoded credentials.** `os.environ` only.
- **Read-only by default.** Mutating operations (POST, DELETE, INSERT, DROP) require explicit admin approval in the QA review.
- **Transform, don't pass through.** Scripts should return purposeful data shapes, not raw API responses. Remove fields agents don't need. Add business labels. The goal is that the tool's output can go directly into agent context without noise.
- **Linting:** `ruff` with line length 100.

```bash
pip install -e ".[dev]"
ruff check .
pytest
```

---

## For Agencies: Managing Multiple Client Deployments

```bash
# New client
copier copy gh:your-org/agent-gateway ./client-acme

# Pull upstream improvements into an existing client repo
cd client-acme && copier update
```

Each client repo is independent. Improvements to the master template can be selectively pulled into each client with `copier update`.

---

## License

MIT — see [LICENSE](LICENSE).
