Curated Context Architecture: MVP Initialization Blueprint

1. System Overview

This hybrid architecture bridges the gap between decentralized employee experimentation and centralized enterprise governance. It employs an Agentic GitOps Pipeline.

Rather than forcing all traffic through a restrictive gateway on day one, it allows employees to use local MCP servers (Stripe, Snowflake, CRM) for rapid R&D. When an employee discovers a valuable workflow using these local MCPs, their local AI automatically codifies the interaction into two distinct assets:

A Python Tool: The executable code that performs the data extraction and cleaning.

A Markdown Skill: The SOP (Standard Operating Procedure) that teaches the agent when to use the tool.

Once approved, the Admin migrates the Python Tool to the Remote Gateway as a centralized MCP tool, and the Skill remains in the shared repository for the whole team's local agents to reference.

Key MVP Decisions:

Language: Python (for both local context tools and the remote FastAPI MCP server).

Version Control: GitHub Monorepo with Sparse-Checkout for local users.

Flexibility: Employees configure raw MCPs locally via .mcp.json or the claude mcp add CLI.

Deployment: Manual merges and migrations by the Admin.

2. Repository Architecture & Git Setup

The system operates as a single monorepo to maintain unified version control, but strictly isolates the remote infrastructure from the local employee sandboxes.

2.1 Directory Structure

revops-agent-monorepo/
│
├── .github/
│   └── workflows/
│       └── qa_agent_review.yml       # Triggers the Remote QA Agent on PRs
│
├── local-workspace/                  # EMPLOYEES ONLY PULL THIS FOLDER
│   ├── .mcp.json                     # Local workspace MCP configurations
│   ├── instructions.md               # The Local Master Prompt
│   ├── tools/                        # Python scripts (The "Muscle")
│   ├── skills/                       # Markdown SOPs (The "Brain")
│   └── context/                      # Brand guidelines, templates
│
└── remote-gateway/                   # HOSTED SECURELY (DO NOT PULL LOCALLY)
    ├── core/
    │   └── mcp_server.py             # Central Python/FastAPI MCP server
    ├── official_tools/               # Promoted, QA-approved Python tools
    └── prompts/
        └── qa_agent_instructions.md  # The Remote QA Master Prompt


2.2 Employee Onboarding (Sparse-Checkout)

To ensure employees do not download sensitive remote routing logic, they must initialize their local environment using Git Sparse-Checkout.

Provide this exact script to the 4-person team:

# 1. Clone the repository without checking out the files
git clone --no-checkout [https://github.com/yourorg/revops-agent-monorepo.git](https://github.com/yourorg/revops-agent-monorepo.git)
cd revops-agent-monorepo

# 2. Enable cone-mode sparse-checkout (optimized for directories)
git sparse-checkout init --cone

# 3. Restrict the checkout strictly to the local sandbox
git sparse-checkout set local-workspace

# 4. Pull the files
git checkout main


3. The Local Workspace (The R&D Sandbox)

Employees are encouraged to connect raw tools locally using claude mcp add. This allows them to experiment with company data.

3.1 The Local Master Prompt (local-workspace/instructions.md)

This instruction set forces Claude to transition from just "using" local tools to "codifying" successful tool usage into the formal Tools & Skills structure.

Content:

System Identity & Core Directive
You are an autonomous RevOps Context Manager and Workflow Developer. You have access to local MCP tools (configured in .mcp.json). Your job is to answer user queries, but more importantly, to codify repetitive or complex interactions into reusable Python Tools and Markdown Skills.

The Incubation Loop (Tools & Skills):

When a user asks a question, use your available local MCP tools (e.g., Stripe, CRM) to fetch the data.

If the data is raw, noisy, or requires multiple tool calls, do not just answer the user.

Create the Tool: Write a well-documented Python script in local-workspace/tools/. It must include type hints and a clear docstring so it can be easily converted into a formal MCP tool later. Run it locally via terminal to verify it works.

Create the Skill: Write a Markdown file in local-workspace/skills/ (e.g., evaluate_churn.md). This file should explain to other agents what business problem this solves, when to trigger the Python tool you just wrote, and how to interpret the output.

Present the final synthesized answer to the user.

The Auto-Push Git Protocol (CRITICAL):
You are authenticated to GitHub. Whenever you successfully create or modify a Tool/Skill pair, you must automatically push it to the repository.

Run git checkout -b feature/[username]-[tool-name]

Run git add local-workspace/tools/[your_script.py] local-workspace/skills/[your_skill.md]

Run git commit -m "feat: codified [tool-name] tool and skill"

Run git push origin [branch-name]

Inform the user: "I codified this sequence into a Python Tool and a Markdown Skill, and pushed it to your branch for review."

4. The Remote Gateway (Centralized Orchestrator)

The Remote Gateway is where proven Python tools go to become permanent, governed infrastructure.

4.1 The Gateway Migration Strategy

When a local Python script from an employee proves valuable:

The Admin reviews the PR containing the new tools/script.py and skills/script.md.

The Admin ports the Python tool into mcp_server.py, wrapping it in the official Python MCP SDK decorator (e.g., @mcp.tool()). The docstrings Claude generated locally become the MCP tool descriptions.

The Admin provisions the necessary API keys directly into the Remote Gateway.

The Markdown Skill is merged into the main branch.

The Result: The entire team pulls main. Their local Claude instances read the Markdown Skill, which tells them to use the new Remote Gateway MCP tool instead of their raw local connections.

CRITICAL GUARDRAIL: The mcp_server.py file must enforce Read-Only logic for all newly migrated data-fetching tools unless explicit write-permissions are structurally required and approved by the Admin.

5. The Agentic CI/CD Pipeline

When a local Claude instance pushes a new Python tool to GitHub, it triggers an automated architectural review.

5.1 The Remote QA Agent Prompt (remote-gateway/prompts/qa_agent_instructions.md)

This prompt is utilized by an LLM via a GitHub Action triggered on PR creation.

Content:

System Identity & Core Directive
You are the AI Architecture Reviewer for our RevOps Monorepo. A local agent has just pushed a new Python Tool and Markdown Skill to a feature branch. Your job is to review the code, ensure it is safe for the central middleware, and leave a detailed PR comment. You do not have permission to merge.

MVP Evaluation Criteria:

Safety Check: Does the Python script contain mutating commands (DROP, INSERT, POST, DELETE)? Reject the code if it contains unauthorized write actions.

Security Check: Does this script contain hardcoded API keys or credentials? (It should rely on environment variables).

Tool Quality: Is the Python function clearly defined with type hints and a comprehensive docstring? (This is required for fast MCP migration).

Skill Quality: Does the Markdown skill clearly explain the business use-case for the tool?

Required Action:
Leave a comment on the Pull Request.

If it fails safety/security: Output a 🛑 WARNING, explain the exact violation, and reject the code.

If it passes: Output "✅ Passed Automated QA." Then, provide a summary for the Admin detailing how easily the Python script can be wrapped into an @mcp.tool().

6. The Usage-Driven Lifecycle (Day-to-Day Operations)

Local Incubation: The employee installs the raw Stripe MCP locally via Claude Code.

Sandbox R&D: The employee asks for churn metrics. Claude uses the local Stripe MCP to get the answer.

Codification: Following its master prompt, Claude creates tools/stripe_churn.py (the code) and skills/evaluate_churn.md (the instructions on when/how to use the code).

Auto-Version Control: Claude automatically commits both files to a new branch and pushes to GitHub.

Automated QA: The GitHub Action QA Agent reviews the PR, ensuring the code is secure and properly documented for MCP translation.

Centralized Migration (Admin): You review the PR. You copy the function from tools/stripe_churn.py into remote-gateway/core/mcp_server.py and decorate it as an official MCP tool. You merge the Markdown Skill into main.

Fleet Upgrade: The entire team runs git pull. Their local agents read the newly merged Skill, which instructs them to query the Remote Gateway for churn calculations moving forward.