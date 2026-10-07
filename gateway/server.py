"""Read-only MCP gateway foundation. No identity or authority mutations."""
from datetime import datetime, timezone
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "UCII Alexa Authority Gateway",
    host="127.0.0.1",
    port=8006,
    stateless_http=True,
    json_response=True,
)

@mcp.tool()
async def ucii_health() -> dict:
    """Check actual UCII availability; this never grants identity or authority."""
    checked_at = datetime.now(timezone.utc).isoformat()
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=False) as client:
            response = await client.get("http://127.0.0.1:8000/health")
        response.raise_for_status()
        data = response.json()
        if data.get("service") != "UCII" or data.get("status") != "healthy":
            raise ValueError("Unexpected health response")
        return {"ucii": "online", "checked_at": checked_at,
                "version": data.get("version"), "authority": "not evaluated"}
    except (httpx.HTTPError, ValueError):
        return {"ucii": "unavailable", "checked_at": checked_at,
                "authority": "not evaluated"}

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
