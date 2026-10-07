"""Read-only MCP gateway foundation. No identity or authority mutations."""
from datetime import datetime, timezone
import os
from typing import Literal
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


@mcp.tool()
async def ucii_identity(principal: Literal["human", "agent"]) -> dict:
    """Retrieve a configured public identity record, without proving possession."""
    configuration = {
        "human": ("UCII_ALEXA_HUMAN_ID", "HUMAN"),
        "agent": ("UCII_ALEXA_AGENT_ID", "AI_AGENT"),
    }
    variable, identity_type = configuration[principal]
    identity_id = os.environ.get(variable, "")
    from uuid import UUID
    try:
        identity_id = str(UUID(identity_id))
    except ValueError:
        raise ValueError("Identity binding is not configured") from None
    async with httpx.AsyncClient(timeout=10, follow_redirects=False) as client:
        response = await client.get(
            f"http://127.0.0.1:8000/v1/identity/{identity_id}"
        )
    response.raise_for_status()
    data = response.json()
    if (
        data.get("id") != identity_id
        or data.get("identity_type") != identity_type
        or data.get("is_active") is not True
        or not isinstance(data.get("name"), str)
    ):
        raise ValueError("Configured identity is inactive or does not match")
    return {
        "principal": principal,
        "identity_id": identity_id,
        "identity_type": identity_type,
        "name": data["name"],
        "record_status": "ACTIVE",
        "verification": "UNVERIFIED",
        "credential_fingerprint": None,
        "authority": "not evaluated",
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
