"""Canonical JSON integrity envelopes for audit-ready reports."""

import hashlib
import json
from typing import Any


def canonical_json(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def add_integrity_hash(payload: dict[str, Any]) -> dict[str, Any]:
    """Hash report content only; the envelope is excluded to make verification stable."""
    digest = hashlib.sha256(canonical_json(payload)).hexdigest()
    return {**payload, "integrity": {"algorithm": "sha256", "canonicalization": "json-sort-keys-v1", "content_hash": digest}}


def verify_integrity(report: dict[str, Any]) -> bool:
    integrity = report.get("integrity")
    if not isinstance(integrity, dict) or integrity.get("algorithm") != "sha256":
        return False
    content = {key: value for key, value in report.items() if key != "integrity"}
    return hashlib.sha256(canonical_json(content)).hexdigest() == integrity.get("content_hash")
