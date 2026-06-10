"""Tests for the lightweight SQL trace helpers.

Pure-function tests: no Flask, no DB. They verify the small utilities
that format SQL into the rows shown on `/sql-trace` and `/api/sql-trace`.
"""

from zarvent_repuestos.database.sql_trace import (
    build_summary,
    compact_sql,
    extract_tables,
    operation_name,
    summarize_params,
)


class TestExtractTables:
    def test_returns_joined_tables_in_order_without_duplicates(self):
        sql = (
            "SELECT p.part_id, pc.name "
            "FROM part p "
            "JOIN part_category pc ON p.category_id = pc.category_id"
        )

        assert extract_tables(sql) == ["part", "part_category"]

    def test_returns_table_name_for_update_statement(self):
        sql = "UPDATE part SET name = %s WHERE part_id = %s"

        assert extract_tables(sql) == ["part"]


class TestSummarizeParams:
    def test_redacts_when_password_keyword_is_in_sql(self):
        sql = "UPDATE user SET password = %s WHERE user_id = %s"

        assert summarize_params(sql, ("secret", 1)) == "[redacted password fields]"

    def test_redaction_is_case_insensitive(self):
        sql = "UPDATE user SET PASSWORD = %s WHERE user_id = %s"

        assert summarize_params(sql, ("secret", 1)) == "[redacted password fields]"

    def test_returns_short_repr_when_password_keyword_is_absent(self):
        sql = "SELECT * FROM part WHERE part_id = %s"

        assert summarize_params(sql, (42,)) == "(42,)"

    def test_returns_dash_when_params_is_none(self):
        assert summarize_params("SELECT 1", None) == "-"


class TestCompactSql:
    def test_collapses_multiple_whitespace_into_single_spaces(self):
        sql = "SELECT   *\n\tFROM   part\nWHERE  part_id = 1"

        assert compact_sql(sql) == "SELECT * FROM part WHERE part_id = 1"


class TestOperationName:
    def test_returns_select_keyword(self):
        assert operation_name("  SELECT * FROM part") == "SELECT"

    def test_returns_insert_keyword(self):
        assert operation_name("INSERT INTO part (name) VALUES (%s)") == "INSERT"


class TestBuildSummary:
    def test_counts_total_errors_and_operations(self):
        entries = [
            {"operation": "SELECT", "status": "OK", "tables": ["part"]},
            {"operation": "INSERT", "status": "OK", "tables": ["part"]},
            {"operation": "UPDATE", "status": "ERROR", "tables": ["part_category"]},
        ]

        summary = build_summary(entries)

        assert summary["total"] == 3
        assert summary["errors"] == 1
        assert summary["operations"] == {
            "SELECT": 1, "INSERT": 1, "UPDATE": 1, "DELETE": 0,
        }
