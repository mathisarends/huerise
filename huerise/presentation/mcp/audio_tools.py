import importlib.util

if importlib.util.find_spec("fastmcp") is None:
    raise ImportError(
        "MCP support requires 'fastmcp'. Install with: pip install huerise[mcp]"
    )

from fastmcp import Context

from huerise.application.commands import SetVolumeCommand, SetVolumeCommandHandler
from huerise.presentation.mcp.server import mcp


@mcp.tool()
async def set_volume(volume: int, ctx: Context) -> None:
    """Set the alarm audio volume (0–100)."""
    async with ctx.lifespan_context["container"]() as scope:
        handler = await scope.get(SetVolumeCommandHandler)
        await handler.execute(SetVolumeCommand(volume=volume))
