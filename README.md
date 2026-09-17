# AI Data Quality Agent

An explainable data quality agent that detects common pipeline failures, traces likely root causes, masks sensitive values, and produces a concise incident summary for analytics teams.

The project uses synthetic order data and does not contain employer data or proprietary code.

## What it demonstrates

1. Automated checks for duplicate keys, missing values, invalid amounts, stale records, and schema drift
2. Evidence based root cause analysis instead of unverified AI answers
3. PII masking before diagnostic context is sent to a language model
4. Optional Amazon Bedrock summaries with a deterministic local fallback
5. Testable Python components and a simple command line workflow

## Architecture

```text
Synthetic CSV
    |
    v
Data profiler and quality checks
    |
    v
Structured findings with evidence
    |
    +--> PII redaction
    |
    v
Root cause agent
    |
    +--> Local deterministic summary
    +--> Optional Amazon Bedrock summary
    |
    v
Markdown incident report
```

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py --input data/orders.csv --output reports/data_quality_report.md
```

Run the tests:

```bash
pytest
```

## Optional Amazon Bedrock mode

The application works without an API key. To generate the final narrative with Amazon Bedrock, configure AWS credentials and run:

```bash
export USE_BEDROCK=1
export BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
python app.py --input data/orders.csv
```

Only masked evidence is provided to the model. Raw names and email addresses are never included in the prompt.

## Example findings

The synthetic dataset intentionally includes:

1. A duplicate order identifier
2. A missing customer identifier
3. A negative order amount
4. An invalid order status
5. A stale record

The generated report explains each failure, shows supporting evidence, and recommends a concrete next step.

## Repository structure

```text
app.py                         Command line entry point
src/analyzer.py                Data profiling and quality rules
src/agent.py                   Root cause reasoning and Bedrock integration
src/privacy.py                 PII masking utilities
data/orders.csv                Synthetic demonstration data
tests/                         Unit tests
docs/architecture.md           Design decisions and production roadmap
```

## Production roadmap

1. Read dbt test artifacts and Airflow task metadata
2. Add column level lineage from source to dashboard
3. Send incident summaries to Slack
4. Persist findings for trend analysis and alert deduplication
5. Add human approval before remediation actions

## License

MIT
