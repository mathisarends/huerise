import importlib.util

if importlib.util.find_spec("fastmcp") is None:
    raise ImportError(
        "MCP support requires 'fastmcp'. Install with: pip install huerise[mcp]"
    )

from huerise.presentation.mcp.server import mcp

if __name__ == "__main__":
    mcp.run()
