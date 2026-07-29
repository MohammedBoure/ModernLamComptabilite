"""Stage legacy Excel workbooks without importing operational data.

Run this only after taking the database backup required by the rollout plan.
It writes to Import_Batches/Import_Rows, never to accounting or HR tables.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "src"))

from database import data_manager  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Stage legacy FINANCELAM Excel archives.")
    parser.add_argument("paths", nargs="*", type=Path, help="Workbook(s) to stage; defaults to excel/*.xlsx.")
    parser.add_argument("--actor", default="migration-operator", help="Audited user responsible for staging.")
    parser.add_argument("--report-dir", type=Path, default=REPOSITORY / "exports" / "reconciliation")
    args = parser.parse_args()

    workbooks = args.paths or sorted((REPOSITORY / "excel").glob("*.xlsx"))
    if not workbooks:
        parser.error("No .xlsx workbooks were found.")
    args.report_dir.mkdir(parents=True, exist_ok=True)
    for workbook in workbooks:
        result = data_manager.imports.stage_workbook(workbook, args.actor)
        output = args.report_dir / f"{workbook.stem}.reconciliation.json"
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{workbook.name}: {result['status']} (batch {result['batch_id']}) -> {output}")


if __name__ == "__main__":
    main()
