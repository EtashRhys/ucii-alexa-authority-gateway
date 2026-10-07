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


def _agent_sign(message: bytes) -> bytes:
    """Submit a bounded internal challenge to the separate protected signer."""
    import base64
    import json
    import socket
    request = {
        "version": "ucii-local-signer-v1", "operation": "sign",
        "credential_id": os.environ["UCII_ALEXA_AGENT_CREDENTIAL_ID"],
        "algorithm": "ML-DSA-65", "purpose": "operational_sign",
        "message_b64": base64.b64encode(message).decode("ascii"),
    }
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.settimeout(10)
        client.connect("/run/ucii-alexa-signer/signer.sock")
        client.sendall((json.dumps(request) + "\n").encode())
        raw = b""
        while b"\n" not in raw:
            chunk = client.recv(4096)
            if not chunk:
                break
            raw += chunk
            if len(raw) > 65536:
                raise ValueError("Signer response exceeded limit")
    result = json.loads(raw.split(b"\n", 1)[0])
    if result.get("status") != "signed":
        raise ValueError("Protected signer declined verification")
    return base64.b64decode(result["signature_b64"], validate=True)


@mcp.tool()
async def ucii_agent_verify() -> dict:
    """Verify a fresh internally generated agent proof; grants no action authority."""
    import asyncio
    import base64
    import json
    import secrets
    from datetime import timedelta
    from uuid import UUID
    identity_id = str(UUID(os.environ["UCII_ALEXA_AGENT_ID"]))
    fingerprint = os.environ["UCII_ALEXA_AGENT_FINGERPRINT"]
    if len(fingerprint) != 64 or any(c not in "0123456789abcdef" for c in fingerprint):
        raise ValueError("Agent credential binding is invalid")
    now = datetime.now(timezone.utc)
    canonical = lambda value: json.dumps(value, sort_keys=True, separators=(",", ":"))
    message = canonical({
        "purpose": "ucii-alexa-agent-credential-check",
        "identity_id": identity_id, "nonce": secrets.token_urlsafe(32),
        "issued_at": now.isoformat(),
    })
    signature = base64.b64encode(
        await asyncio.to_thread(_agent_sign, message.encode())
    ).decode("ascii")
    path = "/v1/credentials/verify"
    challenge = {
        "nonce": secrets.token_urlsafe(32),
        "subject_identity_id": identity_id,
        "credential_fingerprint": fingerprint,
        "method": "POST", "path": path,
        "issued_at": now.isoformat(),
        "expires_at": (now + timedelta(seconds=60)).isoformat(),
    }
    economic_message = canonical({
        **challenge, "version": "ucii-service-entitlement-proof-v1"
    })
    economic_signature = base64.b64encode(
        await asyncio.to_thread(_agent_sign, economic_message.encode())
    ).decode("ascii")
    presentation = base64.b64encode(canonical({
        "challenge": challenge, "signature": economic_signature
    }).encode()).decode("ascii")
    async with httpx.AsyncClient(timeout=20, follow_redirects=False) as client:
        response = await client.post(
            "http://127.0.0.1:8000" + path,
            headers={"x-ucii-service-entitlement": presentation},
            json={"fingerprint": fingerprint, "message": message, "signature": signature},
        )
    response.raise_for_status()
    result = response.json()
    if (
        result.get("verified") is not True
        or result.get("identity_id") != identity_id
        or result.get("fingerprint") != fingerprint
        or result.get("status") != "ACTIVE"
    ):
        raise ValueError("UCII did not verify the active bound agent credential")
    return {
        "principal": "agent", "identity_id": identity_id,
        "credential_fingerprint": fingerprint, "algorithm": "ML-DSA-65",
        "verification": "VERIFIED", "checked_at": datetime.now(timezone.utc).isoformat(),
        "authority": "not evaluated",
    }

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
