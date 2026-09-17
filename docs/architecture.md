# Architecture and Design Decisions

## Evidence before explanation

The agent does not ask a language model to discover quality issues from raw data. Deterministic checks produce structured findings first. The language model only summarizes verified evidence and recommends a next validation step.

This design reduces hallucination risk and makes every conclusion traceable to a failed check.

## Privacy boundary

Names, email addresses, phone numbers, and addresses are masked before diagnostic evidence reaches the reporting layer. A production implementation should also enforce column level access controls and prevent raw samples from entering logs.

## Human approval

The agent recommends actions but does not modify production data. Remediation should require review by a data owner, especially when a fix changes financial or customer facing outputs.

## Production integration

A production version can ingest dbt test results, Airflow metadata, warehouse query history, and lineage information. The same structured findings can then be delivered to Slack or an incident management system.
