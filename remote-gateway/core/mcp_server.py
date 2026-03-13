"""
RevOps Agent Gateway — Central MCP Server

Hosts promoted, QA-approved tools as official MCP endpoints.
All tools are read-only by default unless explicitly granted write permission.

Run with:
    python remote-gateway/core/mcp_server.py
    # or via mcp CLI:
    mcp run remote-gateway/core/mcp_server.py
"""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    os.environ.get("MCP_SERVER_NAME", "revops-gateway"),
)


@mcp.tool()
def health_check() -> dict:
    """Check that the RevOps Gateway MCP server is running and responsive.

    Returns:
        A dict with status and server name.
    """
    return {
        "status": "ok",
        "server": mcp.name,
    }


# ---------------------------------------------------------------------------
# Promoted tools go below this line.
#
# Migration pattern:
#   1. Copy the function from local-workspace/tools/<script>.py
#   2. Decorate with @mcp.tool()
#   3. Ensure all credentials use os.environ (never hardcode)
#   4. Verify the docstring is clear — it becomes the MCP tool description
#
# Example:
#
#   @mcp.tool()
#   def get_churn_metrics(period: str = "30d") -> dict:
#       """Fetch customer churn metrics from Stripe for a given period.
#
#       Args:
#           period: Time window for churn calculation (e.g., "7d", "30d", "90d").
#
#       Returns:
#           Dict with churn_rate, churned_customers, and total_customers.
#       """
#       ...
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    mcp.run(transport="stdio")
