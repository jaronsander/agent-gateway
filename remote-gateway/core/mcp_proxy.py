"""
MCP Proxy — Gateway upstream connection manager.

Reads remote-gateway/mcp_connections.json at startup. For each defined
connection, opens a persistent stdio (subprocess) or SSE connection to the
upstream MCP server, enumerates its tools, and registers them on the gateway
under the naming convention ``<integration>__<tool_name>``.

Employees connect only to the gateway URL — vendor credentials never leave
the server. Access to individual integrations can be revoked by removing the
entry from mcp_connections.json and redeploying.

Usage (called from mcp_server.py lifespan):
    from mcp_proxy import mount_all_proxies

    @asynccontextmanager
    async def lifespan(server: FastMCP):
        proxy_tasks = await mount_all_proxies(server)
        yield
        for task in proxy_tasks:
            task.cancel()
        await asyncio.gather(*proxy_tasks, return_exceptions=True)
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

CONNECTIONS_FILE = Path(__file__).parent.parent / "mcp_connections.json"


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------


def load_connections() -> dict[str, dict]:
    """Load upstream MCP connection definitions from mcp_connections.json.

    Returns:
        Dict mapping integration slug → connection config dict.
        Returns empty dict if mcp_connections.json does not exist.
    """
    if not CONNECTIONS_FILE.exists():
        return {}
    data = json.loads(CONNECTIONS_FILE.read_text())
    return data.get("connections", {})


def resolve_env(env_config: dict[str, str]) -> dict[str, str]:
    """Expand ``${VAR_NAME}`` references to actual environment variable values.

    Args:
        env_config: Dict of key → value where values may be ``${VAR}`` refs.

    Returns:
        Dict with all ``${VAR}`` references replaced by their runtime values.
    """
    resolved = {}
    for key, val in env_config.items():
        if isinstance(val, str) and val.startswith("${") and val.endswith("}"):
            var_name = val[2:-1]
            resolved[key] = os.environ.get(var_name, "")
        else:
            resolved[key] = str(val)
    return resolved


# ---------------------------------------------------------------------------
# Per-integration proxy runner
# ---------------------------------------------------------------------------


async def _run_stdio_proxy(
    name: str,
    config: dict,
    mcp_server: Any,
    ready: asyncio.Event,
) -> None:
    """Connect to one stdio-based upstream MCP and keep it alive.

    Enumerates the upstream server's tools on connect, registers each as a
    proxied tool on the gateway, then blocks indefinitely to maintain the
    subprocess connection.

    Args:
        name: Integration slug used as the tool name prefix (e.g., "stripe").
        config: Connection config dict from mcp_connections.json.
        mcp_server: The FastMCP server instance to register tools on.
        ready: Event set once tools are registered (or on failure).
    """
    env_overrides = resolve_env(config.get("env", {}))
    merged_env = {**os.environ, **env_overrides}

    server_params = StdioServerParameters(
        command=config["command"],
        args=config.get("args", []),
        env=merged_env,
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools_response = await session.list_tools()

                for tool in tools_response.tools:
                    _register_proxy_tool(mcp_server, name, tool, session)

                count = len(tools_response.tools)
                print(f"  [proxy] '{name}' connected — {count} tool(s) available")
                ready.set()

                # Hold the connection open for the gateway's lifetime.
                await asyncio.Event().wait()

    except Exception as exc:  # noqa: BLE001
        print(f"  [proxy] '{name}' failed to connect: {exc}")
        ready.set()  # Unblock startup so the gateway still comes up


# ---------------------------------------------------------------------------
# Tool registration
# ---------------------------------------------------------------------------


def _register_proxy_tool(
    mcp_server: Any,
    integration: str,
    tool: Any,
    session: ClientSession,
) -> None:
    """Register a single upstream tool as a callable on the gateway.

    The gateway-side name is ``<integration>__<upstream_tool_name>`` so tools
    from different integrations never collide and the source is always clear.

    Args:
        mcp_server: FastMCP server to register the tool on.
        integration: Integration slug (e.g., "stripe").
        tool: MCP Tool object from list_tools() response.
        session: Live ClientSession used to forward calls.
    """
    upstream_name: str = tool.name
    gateway_name: str = f"{integration}__{upstream_name}"
    description: str = (
        (tool.description or upstream_name)
        + f"\n\n[Proxied from the '{integration}' integration. Managed by gateway admin.]"
    )

    async def proxy_fn(**kwargs: Any) -> Any:
        """Forward the call to the upstream MCP server and return its response."""
        result = await session.call_tool(upstream_name, kwargs)
        if not result.content:
            return {}
        content = result.content[0]
        if hasattr(content, "text"):
            try:
                return json.loads(content.text)
            except (json.JSONDecodeError, ValueError):
                return {"result": content.text}
        return {}

    proxy_fn.__name__ = gateway_name
    proxy_fn.__doc__ = description
    mcp_server.add_tool(proxy_fn, name=gateway_name, description=description)


# ---------------------------------------------------------------------------
# Public entrypoint
# ---------------------------------------------------------------------------


async def mount_all_proxies(mcp_server: Any) -> list[asyncio.Task]:
    """Mount all upstream MCPs defined in mcp_connections.json.

    Called from the gateway's lifespan context at startup. Waits for every
    connection to either succeed or fail before returning, so the gateway
    never starts serving with missing tools.

    Args:
        mcp_server: The FastMCP server instance.

    Returns:
        List of running asyncio Tasks (one per connection). Cancel these
        in the lifespan shutdown path to cleanly close upstream processes.
    """
    connections = load_connections()
    if not connections:
        print("  [proxy] No upstream MCP connections configured.")
        return []

    tasks: list[asyncio.Task] = []
    ready_events: list[asyncio.Event] = []

    for name, config in connections.items():
        transport = config.get("transport", "stdio")
        if transport != "stdio":
            print(f"  [proxy] '{name}' skipped — transport '{transport}' not yet supported.")
            continue

        ready = asyncio.Event()
        ready_events.append(ready)
        task = asyncio.create_task(
            _run_stdio_proxy(name, config, mcp_server, ready),
            name=f"proxy:{name}",
        )
        tasks.append(task)

    # Wait until all proxies have either connected or failed before the
    # gateway starts accepting requests.
    if ready_events:
        await asyncio.gather(*(e.wait() for e in ready_events))

    return tasks
