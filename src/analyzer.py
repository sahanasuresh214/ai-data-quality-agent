from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class Finding:
    check: str
    severity: str
    affected_rows: int
    evidence: list[dict[str, Any]]
    likely_cause: str
    recommended_action: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DataQualityAnalyzer:
    required_columns = {
        "order_id",
        "customer_id",
        "customer_email",
        "order_date",
        "amount",
        "status",
    }
    accepted_statuses = {"pending", "paid", "shipped", "cancelled"}

    def analyze(self, frame: pd.DataFrame) -> list[Finding]:
        findings: list[Finding] = []
        findings.extend(self._check_schema(frame))

        if not self.required_columns.issubset(frame.columns):
            return findings

        findings.extend(self._check_duplicates(frame))
        findings.extend(self._check_required_values(frame))
        findings.extend(self._check_amounts(frame))
        findings.extend(self._check_statuses(frame))
        findings.extend(self._check_freshness(frame))
        return findings

    def _check_schema(self, frame: pd.DataFrame) -> list[Finding]:
        missing = sorted(self.required_columns - set(frame.columns))
        if not missing:
            return []
        return [
            Finding(
                check="schema_completeness",
                severity="critical",
                affected_rows=len(frame),
                evidence=[{"missing_columns": missing}],
                likely_cause="The upstream extract changed or required columns were renamed.",
                recommended_action="Compare the source schema with the ingestion contract before processing the file.",
            )
        ]

    def _check_duplicates(self, frame: pd.DataFrame) -> list[Finding]:
        duplicate_rows = frame[frame.duplicated("order_id", keep=False)]
        if duplicate_rows.empty:
            return []
        return [
            Finding(
                check="order_id_uniqueness",
                severity="high",
                affected_rows=len(duplicate_rows),
                evidence=duplicate_rows.head(5).to_dict("records"),
                likely_cause="The source emitted multiple records for the same order grain.",
                recommended_action="Deduplicate using the latest update timestamp and enforce a unique order key test.",
            )
        ]

    def _check_required_values(self, frame: pd.DataFrame) -> list[Finding]:
        missing_rows = frame[frame["customer_id"].isna()]
        if missing_rows.empty:
            return []
        return [
            Finding(
                check="customer_id_not_null",
                severity="high",
                affected_rows=len(missing_rows),
                evidence=missing_rows.head(5).to_dict("records"),
                likely_cause="Customer records were loaded before the customer identifier was assigned.",
                recommended_action="Quarantine incomplete orders and repair the source to customer join.",
            )
        ]

    def _check_amounts(self, frame: pd.DataFrame) -> list[Finding]:
        invalid_rows = frame[frame["amount"] < 0]
        if invalid_rows.empty:
            return []
        return [
            Finding(
                check="amount_non_negative",
                severity="high",
                affected_rows=len(invalid_rows),
                evidence=invalid_rows.head(5).to_dict("records"),
                likely_cause="Refunds or reversals were written into the order amount field without a transaction type.",
                recommended_action="Model refunds separately or add explicit transaction type and sign rules.",
            )
        ]

    def _check_statuses(self, frame: pd.DataFrame) -> list[Finding]:
        invalid_rows = frame[~frame["status"].isin(self.accepted_statuses)]
        if invalid_rows.empty:
            return []
        return [
            Finding(
                check="status_accepted_values",
                severity="medium",
                affected_rows=len(invalid_rows),
                evidence=invalid_rows.head(5).to_dict("records"),
                likely_cause="A new source status was introduced without updating the analytics contract.",
                recommended_action="Confirm the business meaning, update the status mapping, and add an accepted values test.",
            )
        ]

    def _check_freshness(self, frame: pd.DataFrame) -> list[Finding]:
        order_dates = pd.to_datetime(frame["order_date"], errors="coerce", utc=True)
        cutoff = pd.Timestamp(datetime.now(timezone.utc)) - pd.Timedelta(days=365)
        stale_rows = frame[order_dates < cutoff]
        if stale_rows.empty:
            return []
        return [
            Finding(
                check="record_freshness",
                severity="low",
                affected_rows=len(stale_rows),
                evidence=stale_rows.head(5).to_dict("records"),
                likely_cause="Historical records were included in a current period delivery.",
                recommended_action="Confirm the intended reporting window and filter the incremental extract.",
            )
        ]
