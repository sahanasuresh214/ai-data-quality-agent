from __future__ import annotations

import json
import os
from typing import Any

from src.analyzer import Finding
from src.privacy import redact_records


class RootCauseAgent:
    def create_report(self, findings: list[Finding]) -> str:
        safe_findings = [self._safe_finding(finding) for finding in findings]
        if os.getenv("USE_BEDROCK") == "1":
            return self._bedrock_report(safe_findings)
        return self._local_report(safe_findings)

    def _safe_finding(self, finding: Finding) -> dict[str, Any]:
        payload = finding.to_dict()
        payload["evidence"] = redact_records(payload["evidence"])
        return payload

    def _local_report(self, findings: list[dict[str, Any]]) -> str:
        lines = ["# Data Quality Incident Report", ""]
        if not findings:
            return "\n".join(lines + ["No data quality issues were detected.", ""])

        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        ordered = sorted(findings, key=lambda item: severity_order[item["severity"]])

        lines.extend(
            [
                "## Executive summary",
                "",
                f"The agent found {len(ordered)} quality issues. Review critical and high severity findings before publishing the dataset.",
                "",
            ]
        )

        for finding in ordered:
            lines.extend(
                [
                    f"## {finding['check']}",
                    "",
                    f"**Severity:** {finding['severity']}",
                    "",
                    f"**Affected rows:** {finding['affected_rows']}",
                    "",
                    f"**Likely cause:** {finding['likely_cause']}",
                    "",
                    f"**Recommended action:** {finding['recommended_action']}",
                    "",
                    "**Masked evidence:**",
                    "",
                    "```json",
                    json.dumps(finding["evidence"], indent=2, default=str),
                    "```",
                    "",
                ]
            )
        return "\n".join(lines)

    def _bedrock_report(self, findings: list[dict[str, Any]]) -> str:
        try:
            import boto3
        except ImportError as exc:
            raise RuntimeError("Install boto3 to use Amazon Bedrock mode") from exc

        model_id = os.getenv(
            "BEDROCK_MODEL_ID",
            "anthropic.claude-3-5-sonnet-20240620-v1:0",
        )
        client = boto3.client("bedrock-runtime")
        prompt = (
            "You are a data reliability engineer. Summarize these structured findings without inventing facts. "
            "Prioritize by severity, cite the supplied evidence, and recommend the next validation step. "
            "Return Markdown.\n\n"
            + json.dumps(findings, default=str)
        )
        response = client.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"temperature": 0.1, "maxTokens": 1500},
        )
        return response["output"]["message"]["content"][0]["text"]
