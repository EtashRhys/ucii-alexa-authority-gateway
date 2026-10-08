"""Exact action representation. A digest identifies a request, never authority."""
from dataclasses import dataclass
import hashlib
import json
import re
from uuid import UUID

VERSION = "ucii-alexa-action-v1"
ENVIRONMENTS = frozenset({"staging", "production", "not applicable"})


@dataclass(frozen=True, slots=True)
class CanonicalAction:
    subject_identity_id: str
    operation: str
    resource: str
    environment: str
    artifact_digest: str | None = None

    def __post_init__(self):
        if not isinstance(self.subject_identity_id, str) or str(UUID(self.subject_identity_id)) != self.subject_identity_id:
            raise ValueError("A canonical UCII subject identity is required")
        if not isinstance(self.operation, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.:-]{0,127}", self.operation):
            raise ValueError("One exact operation is required")
        if (not isinstance(self.resource, str) or not self.resource or len(self.resource) > 512
                or self.resource != self.resource.strip() or any(ord(c) < 32 or ord(c) == 127 for c in self.resource)
                or any(c in self.resource for c in "*?")):
            raise ValueError("One explicit resource is required")
        if not isinstance(self.environment, str) or self.environment not in ENVIRONMENTS:
            raise ValueError("An explicit environment is required")
        if self.artifact_digest is not None and (not isinstance(self.artifact_digest, str)
                or not re.fullmatch(r"sha256:[a-f0-9]{64}", self.artifact_digest)):
            raise ValueError("Artifact must be an exact lowercase SHA-256 digest")
        if self.operation == "infrastructure.deploy" and (
                self.environment == "not applicable" or self.artifact_digest is None):
            raise ValueError("Deployment requires an environment and exact artifact digest")

    @classmethod
    def from_proposal(cls, proposal, *, subject_identity_id):
        # Derive the subject on the server, never from browser/model input.
        if not isinstance(proposal, dict) or set(proposal) not in (
                {"operation", "resource", "environment"},
                {"operation", "resource", "environment", "artifact_digest"}):
            raise ValueError("Proposal fields do not match the action contract")
        return cls(subject_identity_id=subject_identity_id, **proposal)

    def canonical_message(self):
        return json.dumps({
            "version": VERSION,
            "subject_identity_id": self.subject_identity_id,
            "operation": self.operation,
            "resource": self.resource,
            "environment": self.environment,
            "artifact_digest": self.artifact_digest,
        }, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def digest(self):
        return "sha256:" + hashlib.sha256(self.canonical_message().encode("utf-8")).hexdigest()
