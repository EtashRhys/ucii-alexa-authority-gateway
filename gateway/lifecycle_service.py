"""Alexa-only lifecycle composition: HUMAN session plus root-controlled permit."""
import json
import os
from pathlib import Path
import urllib.request

from pq_auth.auth import models as _auth_models
from pq_auth.config import SessionLocal
from ucii_agents.controller_lifecycle_credentials import load_controller_lifecycle_credential
from ucii_agents.controller_lifecycle_service import controller_lifecycle_ipc_group_gid
from ucii_agents.controller_lifecycle_daemon import ProtectedControllerLifecycleDaemon
from ucii_agents.controller_lifecycle_authorization import (
    load_controller_lifecycle_grant_authorization,
    load_controller_lifecycle_authorization,
)
from ucii_agents.controller_lifecycle_authorization_consumption import (
    consume_controller_lifecycle_grant_authorization,
    consume_controller_lifecycle_authorization,
)
from ucii_agents.provenance_recorder import ProvenanceRecorder


class AlexaLifecycleDaemon(ProtectedControllerLifecycleDaemon):
    def verify_human(self, token):
        if not isinstance(token, str) or not token or len(token) > 8192:
            raise ValueError("HUMAN session required")
        request = urllib.request.Request(
            "http://127.0.0.1:8000/v1/auth/session",
            headers={"Authorization": "Bearer " + token},
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.load(response)
        if data.get("identity_id") != os.environ["UCII_ALEXA_HUMAN_ID"]:
            raise ValueError("HUMAN identity mismatch")

    def handle_request(self, request):
        try:
            if not isinstance(request, dict):
                raise ValueError("Invalid request")
            token = request.get("human_token")
            intent = {k: v for k, v in request.items() if k != "human_token"}
            operation = intent.get("operation")
            if operation == "grant_delegated_authority":
                operations, granted_by = self._validate_grant_request(intent)
                if granted_by != os.environ["UCII_ALEXA_HUMAN_ID"]:
                    raise ValueError("Grant provenance mismatch")
            elif operation == "revoke_delegated_authority":
                authority_id, reason = self._validate_request(intent)
            else:
                raise ValueError("Unsupported operation")
            # Authenticate independently inside the custody process.
            self.verify_human(token)
            directory = Path("/etc/ucii-alexa-lifecycle")
            recorder = ProvenanceRecorder(
                Path("/var/lib/ucii-alexa-lifecycle/provenance.jsonl")
            )
            if operation == "grant_delegated_authority":
                authorization = load_controller_lifecycle_grant_authorization(
                    directory / "grant-authorization.json"
                )
                consume_controller_lifecycle_grant_authorization(
                    recorder=recorder, authorization=authorization,
                    identity_id=self.identity_id,
                    allowed_operations=operations, granted_by=granted_by,
                )
            else:
                authorization = load_controller_lifecycle_authorization(
                    directory / "revoke-authorization.json"
                )
                consume_controller_lifecycle_authorization(
                    recorder=recorder, authorization=authorization,
                    identity_id=self.identity_id,
                    authority_id=authority_id, reason=reason,
                )
            # Existing UCII daemon verifies controller possession and mutates UCII.
            return super().handle_request(intent)
        except Exception:
            # Tokens, controller credentials and upstream errors stay private.
            return {"status": "denied", "reason": "Protected HUMAN approval or one-use operator authorization not established"}


def main():
    credential = load_controller_lifecycle_credential(name="alexa-agent-controller")
    if credential.identity_id != os.environ["UCII_ALEXA_AGENT_ID"]:
        raise RuntimeError("Alexa controller binding mismatch")
    daemon = AlexaLifecycleDaemon(
        socket_path="/run/ucii-alexa-lifecycle/lifecycle.sock",
        credential=credential, session_factory=SessionLocal,
        directory_mode=0o750, socket_mode=0o660,
        ipc_group_gid=controller_lifecycle_ipc_group_gid(),
    )
    daemon.serve_forever()


if __name__ == "__main__":
    main()
