"""Official export generation and immutable export-history registration."""

from __future__ import annotations

import csv
import json
from datetime import datetime

from .activity_log_service import ActivityLogService
from pathlib import Path
from typing import Iterable, Mapping


class ExportService:
    def __init__(self, db_instance):
        self.db = db_instance

    def _actor(self, actor_username=None):
        return actor_username or getattr(self.db, "current_actor", None) or "system"

    def period_id_for(self, month=None, year=None):
        if not month or not year:
            return None
        row = self.db.fetch_one(
            "SELECT id_period FROM Accounting_Periods WHERE mois = %s AND annee = %s", (month, year)
        )
        return row["id_period"] if row else None

    def register_export(self, report_name, export_format, file_path, actor_username=None, period_id=None, official=True):
        path = Path(file_path).resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        actor = self._actor(actor_username)
        success, export_id = self.db.execute(
            """INSERT INTO Export_History
               (report_name, period_id, export_format, file_path, generated_by, is_official)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (report_name, period_id, export_format, str(path), actor, int(bool(official))),
        )
        if success:
            ActivityLogService(self.db).record(
                actor, "REPORT_EXPORTED", "Export_History", export_id, period_id,
                new_values={"report_name": report_name, "format": export_format, "path": str(path)},
                event_category="EXPORT", message="Official report export generated.",
            )
        return success, export_id

    def export_csv(self, output_path, rows: Iterable[Mapping], report_name, actor_username=None, period_id=None):
        path = Path(output_path)
        materialized = list(rows)
        fieldnames = list(materialized[0].keys()) if materialized else []
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(materialized)
        self.register_export(report_name, "CSV", path, actor_username, period_id)
        return path

    def export_xlsx(self, output_path, rows: Iterable[Mapping], report_name, actor_username=None, period_id=None):
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font
        except ImportError as error:
            raise RuntimeError("openpyxl is required for Excel export.") from error
        path = Path(output_path)
        materialized = list(rows)
        fields = list(materialized[0].keys()) if materialized else []
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = report_name[:31] or "Report"
        sheet.append(fields)
        for cell in sheet[1]:
            cell.font = Font(bold=True)
        for row in materialized:
            sheet.append([row.get(field) for field in fields])
        sheet.freeze_panes = "A2"
        path.parent.mkdir(parents=True, exist_ok=True)
        workbook.save(path)
        self.register_export(report_name, "XLSX", path, actor_username, period_id)
        return path

    def official_filename(self, report_code, extension, month=None, year=None):
        suffix = f"_{int(year):04d}-{int(month):02d}" if month and year else ""
        return f"{report_code}{suffix}_{datetime.now():%Y%m%d_%H%M%S}.{extension.lstrip('.')}"
