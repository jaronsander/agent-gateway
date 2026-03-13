# RevOps Agent Gateway

Agentic GitOps monorepo bridging decentralized employee experimentation with centralized enterprise governance.

Employees use local MCP servers for rapid R&D. When a workflow proves valuable, the local AI codifies it into a **Python Tool** (executable code) and a **Markdown Skill** (SOP for agents). Approved tools migrate to the Remote Gateway as governed MCP infrastructure.

## Repository Structure

```
├── local-workspace/          # Employee R&D sandbox (sparse-checkout target)
│   ├── tools/                # Python scripts created by local agents
│   ├── skills/               # Markdown SOPs for agent workflows
│   └── context/              # Brand guidelines, templates, reference docs
│
└── remote-gateway/           # Centralized MCP gateway (admin-only)
    ├── core/mcp_server.py    # FastAPI MCP server with promoted tools
    ├── official_tools/       # QA-approved Python tools
    └── prompts/              # Agent instruction prompts
```

## Employee Onboarding (Sparse-Checkout)

Employees should **only** pull the `local-workspace/` directory. This keeps sensitive remote gateway code off local machines.

```bash
# 1. Clone without checking out files
git clone --no-checkout <YOUR_REPO_URL>
cd <REPO_NAME>

# 2. Enable cone-mode sparse-checkout
git sparse-checkout init --cone

# 3. Restrict checkout to the local sandbox
git sparse-checkout set local-workspace

# 4. Pull the files
git checkout main
```

## Running the Remote Gateway

```bash
# Install dependencies
pip install -e .

# Copy and configure environment variables
cp remote-gateway/.env.example remote-gateway/.env

# Start the MCP server
python remote-gateway/core/mcp_server.py
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run linter
ruff check .

# Run tests
pytest
```
