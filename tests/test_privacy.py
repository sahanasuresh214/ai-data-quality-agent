from src.privacy import redact_records


def test_redaction_masks_email_and_preserves_non_pii():
    records = [{"customer_email": "ava@example.com", "order_id": "1001"}]
    result = redact_records(records)

    assert result[0]["customer_email"].startswith("masked_")
    assert result[0]["customer_email"] != "ava@example.com"
    assert result[0]["order_id"] == "1001"
