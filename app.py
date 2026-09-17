from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.agent import RootCauseAgent
from src.analyzer import DataQualityAnalyzer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze a dataset and generate an explainable quality report.")
    parser.add_argument("--input", default="data/orders.csv", help="Path to the input CSV file")
    parser.add_argument("--output", default="reports/data_quality_report.md", help="Path for the Markdown report")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frame = pd.read_csv(args.input)

    analyzer = DataQualityAnalyzer()
    findings = analyzer.analyze(frame)

    agent = RootCauseAgent()
    report = agent.create_report(findings)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")

    print(f"Analyzed {len(frame)} rows")
    print(f"Found {len(findings)} quality issues")
    print(f"Report written to {output_path}")


if __name__ == "__main__":
    main()
