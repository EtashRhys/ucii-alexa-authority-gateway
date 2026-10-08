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
_SESSION_SECONDS = 900


def install_auth_routes(mcp, sign):
    sessions = {}
    attempts = deque()

    def reply(data, status=200):
        return JSONResponse(data, status_code=status, headers=_HEADERS)

    def prune():
        now = time.monotonic()
        for key in list(sessions):
            if sessions[key]["deadline"] <= now:
                del sessions[key]

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
            if not isinstance(body, dict) or set(body) != {"email", "password"}:
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
                    "http://127.0.0.1:8000/v1/auth/login", json=body,
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
                del sessions[next(iter(sessions))]
            handle = secrets.token_urlsafe(32)
            expires = datetime.now(timezone.utc) + timedelta(seconds=_SESSION_SECONDS)
            sessions[handle] = {
                "token": token, "deadline": time.monotonic() + _SESSION_SECONDS,
                "expires_at": expires.isoformat(),
            }
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
            del sessions[handle]
            return reply({"authentication": "SIGNED_OUT"})
        entry = sessions[handle]
        try:
            await resolve(entry["token"])
        except httpx.HTTPStatusError as error:
            if error.response.status_code == 401:
                sessions.pop(handle, None)
                return reply({"message": "Session expired. Sign in again."}, 401)
            return reply({"message": "UCII session check unavailable."}, 503)
        except Exception:
            return reply({"message": "UCII session check unavailable."}, 503)
        return reply({
            "identity_id": os.environ["UCII_ALEXA_HUMAN_ID"],
            "authentication": "AUTHENTICATED",
            "expires_at": entry["expires_at"],
        })
