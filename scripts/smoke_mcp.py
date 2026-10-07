"""Run a temporary loopback gateway and verify its real MCP protocol."""
import json
from pathlib import Path
import socket
import subprocess
import sys
import time
import httpx

root = Path(__file__).resolve().parents[1]
with socket.socket() as probe:
    try:
        probe.bind(("127.0.0.1", 8006))
    except OSError:
        raise SystemExit("Port 8006 is occupied; stopped without changing services.")

process = subprocess.Popen([sys.executable, str(root / "gateway/server.py")], cwd=root)
try:
    with httpx.Client(timeout=12, headers={
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
    }) as client:
        url = "http://127.0.0.1:8006/mcp"
        for _ in range(50):
            if process.poll() is not None:
                raise RuntimeError("Gateway exited during startup")
            try:
                with socket.create_connection(("127.0.0.1", 8006), timeout=.2):
                    break
            except OSError:
                time.sleep(.2)
        else:
            raise RuntimeError("Gateway startup timeout")

        def rpc(identifier, method, params):
            response = client.post(url, json={
                "jsonrpc": "2.0", "id": identifier,
                "method": method, "params": params,
            })
            response.raise_for_status()
            data = response.json()
            if data.get("id") != identifier or "error" in data:
                raise RuntimeError(f"MCP request failed: {method}")
            return data["result"]

        initialized = rpc(1, "initialize", {
            "protocolVersion": "2025-11-25",
            "capabilities": {},
            "clientInfo": {"name": "ucii-gateway-smoke", "version": "0.1.0"},
        })
        version = initialized["protocolVersion"]
        if version != "2025-11-25":
            raise RuntimeError(f"Unexpected negotiated protocol: {version}")
        client.headers["MCP-Protocol-Version"] = version
        response = client.post(url, json={
            "jsonrpc": "2.0", "method": "notifications/initialized",
        })
        response.raise_for_status()
        tools = rpc(2, "tools/list", {})
        if not any(tool["name"] == "ucii_health" for tool in tools["tools"]):
            raise RuntimeError("Health tool missing")
        result = rpc(3, "tools/call", {"name": "ucii_health", "arguments": {}})
        if result.get("isError"):
            raise RuntimeError("Health tool failed")
        payload = result.get("structuredContent")
        if payload is None:
            payload = json.loads(next(
                item["text"] for item in result["content"] if item["type"] == "text"
            ))
        if payload.get("ucii") != "online":
            raise RuntimeError("UCII did not answer healthy")
        print(json.dumps({
            "result": "PASS", "protocol": version, "tool": "ucii_health",
            "health": payload,
        }, indent=2))
finally:
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
