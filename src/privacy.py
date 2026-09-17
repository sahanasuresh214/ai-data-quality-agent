from __future__ import annotations

import hashlib
from typing import Any


PII_FIELDS = {"customer_email", "customer_name", "phone", "address"}


def mask_value(value: Any) -> str:
    digest = hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:10]
    return f"masked_{digest}"


def redact_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    redacted: list[dict[str, Any]] = []
    for record in records:
        redacted.append(
            {
                key: mask_value(value) if key in PII_FIELDS and value is not None else value
                for key, value in record.items()
            }
        )
    return redacted
