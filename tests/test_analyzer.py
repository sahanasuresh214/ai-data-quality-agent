import pandas as pd

from src.analyzer import DataQualityAnalyzer


def test_analyzer_detects_expected_issues():
    frame = pd.read_csv("data/orders.csv")
    findings = DataQualityAnalyzer().analyze(frame)
    checks = {finding.check for finding in findings}

    assert checks == {
        "order_id_uniqueness",
        "customer_id_not_null",
        "amount_non_negative",
        "status_accepted_values",
        "record_freshness",
    }


def test_valid_dataset_has_no_findings():
    frame = pd.DataFrame(
        [
            {
                "order_id": "1001",
                "customer_id": "C001",
                "customer_email": "ava@example.com",
                "order_date": "2026-09-10",
                "amount": 25.0,
                "status": "paid",
            }
        ]
    )

    assert DataQualityAnalyzer().analyze(frame) == []
