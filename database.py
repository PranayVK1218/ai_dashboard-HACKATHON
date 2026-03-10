"""
InsightAI — database.py
SQLite-based data access layer for India Life Insurance Claims.
Loads the CSV into an in-memory SQLite DB for fast querying.
"""
import sqlite3
import csv
import os
from typing import Optional


class DatabaseEngine:
    def __init__(self, csv_path: str = "../data/sales_data.csv"):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._load_csv(csv_path)

    def _load_csv(self, path: str):
        """Load the CSV into an in-memory SQLite table."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Data file not found: {path}")

        with open(path, encoding="latin1") as f:
            reader = csv.DictReader(f)
            rows = [r for r in reader]

        # Clean rows
        clean = [
            r for r in rows
            if r.get("life_insurer") and r["life_insurer"].strip()
            and len(r["life_insurer"]) < 40
            and r.get("year") and "-" in str(r.get("year", ""))
        ]

        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS insurance_claims (
                life_insurer TEXT,
                year TEXT,
                claims_pending_start_no REAL,
                claims_intimated_no REAL,
                total_claims_no REAL,
                total_claims_amt REAL,
                claims_paid_no REAL,
                claims_paid_amt REAL,
                claims_repudiated_no REAL,
                claims_repudiated_amt REAL,
                claims_rejected_no REAL,
                claims_rejected_amt REAL,
                claims_pending_end_no REAL,
                claims_paid_ratio_no REAL,
                claims_paid_ratio_amt REAL,
                claims_repudiated_rejected_ratio_no REAL,
                claims_pending_ratio_no REAL,
                category TEXT
            )
        """)

        def safe_float(v):
            try:
                return float(v) if v and v.strip() else 0.0
            except (ValueError, AttributeError):
                return 0.0

        for r in clean:
            cursor.execute("""
                INSERT INTO insurance_claims VALUES (
                    ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
                )
            """, (
                r.get("life_insurer", "").strip(),
                r.get("year", "").strip(),
                safe_float(r.get("claims_pending_start_no")),
                safe_float(r.get("claims_intimated_no")),
                safe_float(r.get("total_claims_no")),
                safe_float(r.get("total_claims_amt")),
                safe_float(r.get("claims_paid_no")),
                safe_float(r.get("claims_paid_amt")),
                safe_float(r.get("claims_repudiated_no")),
                safe_float(r.get("claims_repudiated_amt")),
                safe_float(r.get("claims_rejected_no")),
                safe_float(r.get("claims_rejected_amt")),
                safe_float(r.get("claims_pending_end_no")),
                safe_float(r.get("claims_paid_ratio_no")),
                safe_float(r.get("claims_paid_ratio_amt")),
                safe_float(r.get("claims_repudiated_rejected_ratio_no")),
                safe_float(r.get("claims_pending_ratio_no")),
                r.get("category", "").strip(),
            ))

        self.conn.commit()
        print(f"[DB] Loaded {len(clean)} records into insurance_claims table.")

    def execute_sql(self, sql: str) -> list:
        """Run arbitrary SQL and return list of dicts."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            cols = [d[0] for d in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as e:
            return [{"error": str(e)}]

    def query(self, year: Optional[str] = None, insurer: Optional[str] = None) -> list:
        """Return filtered records."""
        sql = "SELECT * FROM insurance_claims WHERE 1=1"
        params = []
        if year and year != "all":
            sql += " AND year = ?"
            params.append(year)
        if insurer and insurer != "all":
            sql += " AND life_insurer = ?"
            params.append(insurer)
        sql += " ORDER BY claims_paid_ratio_no DESC"

        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        cols = [d[0] for d in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

    def get_kpis(self, year: Optional[str] = None) -> dict:
        """Return aggregated KPI metrics."""
        base = "FROM insurance_claims WHERE length(life_insurer) > 4"
        params = []
        if year and year != "all":
            base += " AND year = ?"
            params.append(year)

        cursor = self.conn.cursor()

        cursor.execute(f"SELECT SUM(total_claims_no), SUM(claims_paid_no), SUM(claims_paid_amt), AVG(claims_paid_ratio_no) {base}", params)
        row = cursor.fetchone()

        return {
            "total_claims": int(row[0] or 0),
            "claims_paid": int(row[1] or 0),
            "amount_paid_crore": round(row[2] or 0, 2),
            "avg_paid_ratio_pct": round((row[3] or 0) * 100, 2)
        }

    def get_trend(self) -> list:
        """Year-over-year aggregated data."""
        sql = """
            SELECT year,
                   SUM(total_claims_no) as total_claims,
                   SUM(claims_paid_no) as claims_paid,
                   SUM(claims_paid_amt) as amount_paid,
                   ROUND(AVG(claims_paid_ratio_no)*100, 2) as avg_ratio
            FROM insurance_claims
            WHERE length(life_insurer) > 4
            GROUP BY year
            ORDER BY year
        """
        return self.execute_sql(sql)

    def get_insurers(self) -> list:
        """All unique insurer names."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT DISTINCT life_insurer FROM insurance_claims "
            "WHERE length(life_insurer) > 4 ORDER BY life_insurer"
        )
        return [row[0] for row in cursor.fetchall()]

    def get_context_summary(self, year: Optional[str] = None, insurer: Optional[str] = None) -> dict:
        """Summary stats for AI context."""
        params = []
        where = "WHERE length(life_insurer) > 4"
        if year and year != "all":
            where += " AND year = ?"
            params.append(year)
        if insurer and insurer != "all":
            where += " AND life_insurer = ?"
            params.append(insurer)

        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT COUNT(*), SUM(total_claims_no), ROUND(AVG(claims_paid_ratio_no)*100,2) "
            f"FROM insurance_claims {where}", params
        )
        row = cursor.fetchone()
        return {
            "year": year or "all",
            "total_records": row[0],
            "total_claims": int(row[1] or 0),
            "avg_paid_ratio": row[2]
        }

    def count(self) -> int:
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM insurance_claims")
        return cursor.fetchone()[0]