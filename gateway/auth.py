"""Browser login adapter. No passwords or UCII tokens enter MCP tools."""
import asyncio
import base64
from collections import deque
from datetime import datetime, timedelta, timezone
import json
import os
import secrets
import time

import httpx
from starlette.responses import JSONResponse

_HEADERS = {"Cache-Control": "no-store"}
_SESSION_MINUTES = (15, 60, 240)


def _token_expiry(token):
    # Scheduling hint only; UCII independently verifies identity and signature.
    payload = token.split(".")[1]
    value = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))["exp"]
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 < value < 10**12:
        raise ValueError("Invalid token expiry")
    return value



def _lifecycle_exchange(intent):
    import socket
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.settimeout(35)
        client.connect("/run/ucii-alexa-lifecycle/lifecycle.sock")
        client.sendall((json.dumps(intent) + "\n").encode("utf-8"))
        raw = b""
        while b"\n" not in raw:
            chunk = client.recv(4096)
            if not chunk:
                break
            raw += chunk
            if len(raw) > 16384:
                raise ValueError("Response exceeded bound")
    result = json.loads(raw.split(b"\n", 1)[0])
    if not isinstance(result, dict):
        raise ValueError("Invalid lifecycle response")
    return result

def install_auth_routes(mcp, sign):
    sessions = {}
    attempts = deque()

    def reply(data, status=200):
        return JSONResponse(data, status_code=status, headers=_HEADERS)

    def prune():
        now = time.monotonic()
        for key in list(sessions):
            if sessions[key]["deadline"] <= now:
                discard(key)

    def discard(handle):
        entry = sessions.pop(handle, None)
        if entry and entry.get("renewal") and entry["renewal"] is not asyncio.current_task():
            entry["renewal"].cancel()

    async def renew(handle, entry):
        # Renew even with a closed browser. Never extend the chosen deadline.
        try:
            while sessions.get(handle) is entry:
                delay = min(entry["token_expiry"] - time.time() - 300,
                            entry["deadline"] - time.monotonic())
                await asyncio.sleep(max(0, delay))
                async with entry["lock"]:
                    if sessions.get(handle) is not entry:
                        return
                    if entry["deadline"] <= time.monotonic():
                        discard(handle)
                        return
                    await resolve(entry["token"])
                    async with httpx.AsyncClient(timeout=30, follow_redirects=False) as client:
                        response = await client.post(
                            "http://127.0.0.1:8000/v1/auth/refresh",
                            json={"token": entry["token"]},
                        )
                    response.raise_for_status()
                    token = response.json()["access_token"]
                    await resolve(token)
                    expiry = _token_expiry(token)
                    if expiry <= time.time() + 300:
                        raise ValueError("Renewal lifetime too short")
                    if sessions.get(handle) is not entry:
                        return
                    entry.update(token=token, token_expiry=expiry)
        except asyncio.CancelledError:
            raise
        except Exception:
            # Ambiguous refresh cannot be retried with a consumed token.
            discard(handle)

    async def resolve(token):
        async with httpx.AsyncClient(timeout=30, follow_redirects=False) as client:
            response = await client.get(
                "http://127.0.0.1:8000/v1/auth/session",
                headers={"Authorization": "Bearer " + token},
            )
        response.raise_for_status()
        data = response.json()
        if data.get("identity_id") != os.environ["UCII_ALEXA_HUMAN_ID"]:
            raise ValueError("Login identity mismatch")
        return data

    async def economic_proof():
        now = datetime.now(timezone.utc)
        challenge = {
            "nonce": secrets.token_urlsafe(32),
            "subject_identity_id": os.environ["UCII_ALEXA_AGENT_ID"],
            "credential_fingerprint": os.environ["UCII_ALEXA_AGENT_FINGERPRINT"],
            "method": "POST", "path": "/v1/auth/login",
            "issued_at": now.isoformat(),
            "expires_at": (now + timedelta(seconds=60)).isoformat(),
        }
        canonical = lambda value: json.dumps(value, sort_keys=True, separators=(",", ":"))
        message = canonical({
            **challenge, "version": "ucii-service-entitlement-proof-v1",
        })
        signature = await asyncio.to_thread(sign, message.encode())
        return base64.b64encode(canonical({
            "challenge": challenge,
            "signature": base64.b64encode(signature).decode("ascii"),
        }).encode()).decode("ascii")

    @mcp.custom_route("/auth/login", methods=["POST"])
    async def login(request):
        # Global bound is deliberate for this single-owner integration.
        now = time.monotonic()
        while attempts and attempts[0] <= now - 60:
            attempts.popleft()
        if len(attempts) >= 5:
            return reply({"message": "Too many login attempts. Try again in a minute."}, 429)
        attempts.append(now)
        if request.headers.get("content-type", "").split(";")[0].strip() != "application/json":
            return reply({"message": "JSON required."}, 415)
        raw = await request.body()
        if len(raw) > 4096:
            return reply({"message": "Login request too large."}, 413)
        try:
            body = json.loads(raw)
            if not isinstance(body, dict) or set(body) not in ({"email", "password"}, {"email", "password", "duration_minutes"}):
                raise ValueError()
            minutes = body.get("duration_minutes", 15)
            if isinstance(minutes, bool) or not isinstance(minutes, int) or minutes not in _SESSION_MINUTES:
                raise ValueError()
            if not all(isinstance(body[k], str) and body[k] for k in ("email", "password")):
                raise ValueError()
            if len(body["email"]) > 254 or len(body["password"]) > 1024:
                raise ValueError()
        except (ValueError, TypeError):
            return reply({"message": "Enter your email and password."}, 400)
        try:
            presentation = await economic_proof()
            async with httpx.AsyncClient(timeout=120, follow_redirects=False) as client:
                response = await client.post(
                    "http://127.0.0.1:8000/v1/auth/login",
                    json={key: body[key] for key in ("email", "password")},
                    headers={"x-ucii-service-entitlement": presentation},
                )
            if response.status_code == 401:
                return reply({"message": "Login could not be verified."}, 401)
            response.raise_for_status()
            token = response.json()["access_token"]
            if not isinstance(token, str) or not token:
                raise ValueError()
            await resolve(token)
            prune()
            if len(sessions) >= 32:
                discard(next(iter(sessions)))
            handle = secrets.token_urlsafe(32)
            expires = datetime.now(timezone.utc) + timedelta(minutes=minutes)
            sessions[handle] = {
                "token": token, "deadline": time.monotonic() + minutes * 60,
                "expires_at": expires.isoformat(),
                "token_expiry": _token_expiry(token), "lock": asyncio.Lock(),
            }
            sessions[handle]["renewal"] = asyncio.create_task(renew(handle, sessions[handle]))
            return reply({
                "session": handle, "identity_id": os.environ["UCII_ALEXA_HUMAN_ID"],
                "authentication": "AUTHENTICATED", "expires_at": expires.isoformat(),
            })
        except Exception:
            # Never include upstream errors, tokens or credentials in diagnostics.
            return reply({"message": "UCII login is unavailable. No authority changed."}, 503)

    @mcp.custom_route("/auth/session", methods=["GET", "DELETE"])
    async def session(request):
        prune()
        header = request.headers.get("authorization", "")
        scheme, separator, handle = header.partition(" ")
        if not separator or scheme.lower() != "bearer" or handle not in sessions:
            return reply({"message": "Authentication required."}, 401)
        if request.method == "DELETE":
            discard(handle)
            return reply({"authentication": "SIGNED_OUT"})
        entry = sessions[handle]
        try:
            async with entry["lock"]:
                if sessions.get(handle) is not entry or entry["deadline"] <= time.monotonic():
                    return reply({"message": "Session expired. Sign in again."}, 401)
                await resolve(entry["token"])
                if sessions.get(handle) is not entry or entry["deadline"] <= time.monotonic():
                    return reply({"message": "Session expired. Sign in again."}, 401)
        except httpx.HTTPStatusError as error:
            if error.response.status_code == 401:
                discard(handle)
                return reply({"message": "Session expired. Sign in again."}, 401)
            return reply({"message": "UCII session check unavailable."}, 503)
        except Exception:
            return reply({"message": "UCII session check unavailable."}, 503)
        return reply({
            "identity_id": os.environ["UCII_ALEXA_HUMAN_ID"],
            "authentication": "AUTHENTICATED",
            "expires_at": entry["expires_at"],
        })


    @mcp.custom_route("/auth/authority", methods=["POST"])
    async def authority(request):
        prune()
        scheme, separator, handle = request.headers.get("authorization", "").partition(" ")
        if not separator or scheme.lower() != "bearer" or handle not in sessions:
            return reply({"message": "Authentication required."}, 401)
        entry = sessions[handle]
        try:
            raw = await request.body()
            if len(raw) > 4096:
                raise ValueError()
            body = json.loads(raw)
            if not isinstance(body, dict):
                raise ValueError()
            command = body.get("command")
            if command == "tool_permission":
                if (set(body) != {"command", "mode", "confirmation"}
                        or body["mode"] not in {"get", "allow", "block"}
                        or body["confirmation"] != ("" if body["mode"] == "get" else "CONFIRM_TOOL_PERMISSION")):
                    raise ValueError()
                intent = {"version":"ucii-alexa-tool-permission-v1",
                    "operation":"sandbox.artifact.verify", "command":body["mode"],
                    "confirmation":body["confirmation"]}
            elif command == "grant":
                import re
                if set(body) != {"command", "operation", "confirmation"}:
                    raise ValueError()
                if body["confirmation"] != "GRANT_OPERATION_AUTHORITY":
                    raise ValueError()
                if not isinstance(body["operation"], str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.:-]{0,127}", body["operation"]):
                    raise ValueError()
                intent = {
                    "version": "ucii-controller-lifecycle-v1",
                    "operation": "grant_delegated_authority",
                    "allowed_operations": [body["operation"]],
                    "granted_by": os.environ["UCII_ALEXA_HUMAN_ID"],
                }
            elif command == "revoke":
                from uuid import UUID
                if set(body) != {"command", "authority_id", "confirmation"}:
                    raise ValueError()
                if body["confirmation"] != "REVOKE_OPERATION_AUTHORITY":
                    raise ValueError()
                intent = {
                    "version": "ucii-controller-lifecycle-v1",
                    "operation": "revoke_delegated_authority",
                    "authority_id": str(UUID(body["authority_id"])),
                    "reason": "human_requested_revocation",
                }
            else:
                raise ValueError()
        except (ValueError, TypeError, KeyError):
            return reply({"message": "Review and explicitly confirm one operation authority change."}, 400)
        async with entry["lock"]:
            try:
                if sessions.get(handle) is not entry or entry["deadline"] <= time.monotonic():
                    return reply({"message": "Session expired. Sign in again."}, 401)
                await resolve(entry["token"])
                if sessions.get(handle) is not entry or entry["deadline"] <= time.monotonic():
                    return reply({"message": "Session expired. Sign in again."}, 401)
            except Exception:
                return reply({"message": "HUMAN session could not be verified. No lifecycle request sent."}, 401)
            try:
                result = await asyncio.to_thread(_lifecycle_exchange, {**intent, "human_token": entry["token"]})
                if command == "tool_permission":
                    permission = result.get("permission", {})
                    if (result.get("status") not in {"saved", "checked"}
                            or permission.get("operation") != "sandbox.artifact.verify"
                            or permission.get("subject_identity_id") != os.environ["UCII_ALEXA_AGENT_ID"]
                            or permission.get("mode") not in {"ALLOWED", "BLOCKED"}):
                        return reply({"message":"Permission not confirmed. Refresh current permission."},503)
                    return reply({"permission":permission})
                if result.get("status") == "denied":
                    return reply({"message": "Protected approval requires a matching, unused operator authorization. No successful change confirmed."}, 403)
                expected = "granted" if command == "grant" else "revoked"
                state = "ACTIVE" if command == "grant" else "REVOKED"
                if (
                    result.get("status") != expected
                    or result.get("identity_id") != os.environ["UCII_ALEXA_AGENT_ID"]
                    or result.get("authority_state") != state
                    or not isinstance(result.get("authority_id"), str)
                    or (command == "grant" and (
                        result.get("allowed_operations") != [body["operation"]]
                        or result.get("granted_by") != os.environ["UCII_ALEXA_HUMAN_ID"]
                    ))
                    or (command == "revoke" and result.get("authority_id") != intent["authority_id"])
                ):
                    raise ValueError()
                # Return public lifecycle metadata only.
                return reply({
                    key: result[key] for key in (
                        "status", "authority_id", "identity_id", "authority_state",
                        "allowed_operations", "granted_by",
                    ) if key in result
                })
            except Exception:
                # A timeout after sending may mean mutation committed: never auto-retry.
                return reply({"message": "Authority change outcome uncertain. Check authority before retrying."}, 503)


    async def authenticated_human(request):
        prune()
        scheme, separator, handle = request.headers.get("authorization", "").partition(" ")
        if not separator or scheme.lower() != "bearer" or handle not in sessions:
            raise ValueError("Authentication required")
        entry = sessions[handle]
        async with entry["lock"]:
            if sessions.get(handle) is not entry or entry["deadline"] <= time.monotonic():
                raise ValueError("Session expired")
            await resolve(entry["token"])
            if sessions.get(handle) is not entry or entry["deadline"] <= time.monotonic():
                raise ValueError("Session expired")
        return os.environ["UCII_ALEXA_HUMAN_ID"]


    async def with_session(request, operation):
        prune()
        scheme, separator, handle = request.headers.get("authorization", "").partition(" ")
        if not separator or scheme.lower() != "bearer" or handle not in sessions:
            raise PermissionError()
        entry = sessions[handle]
        async with entry["lock"]:
            if sessions.get(handle) is not entry or entry["deadline"] <= time.monotonic():
                raise PermissionError()
            try:
                await resolve(entry["token"])
            except Exception:
                raise PermissionError()
            if sessions.get(handle) is not entry or entry["deadline"] <= time.monotonic():
                raise PermissionError()
            return await asyncio.to_thread(operation, entry["token"], os.environ["UCII_ALEXA_HUMAN_ID"])

    from approval_routes import install as install_approval_routes
    install_approval_routes(mcp, with_session, _lifecycle_exchange, reply)

    from proposals import install_proposal_routes
    install_proposal_routes(mcp, authenticated_human)


