"""Lightweight SQL tracing for classroom demonstrations."""

from __future__ import annotations

import os
import re
import time
from collections import deque
from contextvars import ContextVar
from datetime import datetime
from typing import Any


MAX_TRACE_ENTRIES = 80
SQL_TRACE_ENABLED = os.getenv("SQL_TRACE_ENABLED", "").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
_TRACE_ENTRIES: deque[dict[str, Any]] = deque(maxlen=MAX_TRACE_ENTRIES)
_CURRENT_ROUTE: ContextVar[str] = ContextVar("sql_trace_route", default="-")
_CURRENT_METHOD: ContextVar[str] = ContextVar("sql_trace_method", default="-")


def is_sql_trace_enabled() -> bool:
    """Returns whether SQL tracing is enabled for this process."""
    return SQL_TRACE_ENABLED


def get_sql_trace_entries() -> list[dict[str, Any]]:
    """Returns the newest trace entries first."""
    return list(reversed(_TRACE_ENTRIES))


def clear_sql_trace_entries() -> None:
    """Clears the in-memory SQL trace."""
    _TRACE_ENTRIES.clear()


def set_request_context(method: str, route: str) -> None:
    """Stores the current Flask request context for SQL entries."""
    _CURRENT_METHOD.set(method)
    _CURRENT_ROUTE.set(route)


def clear_request_context() -> None:
    """Clears request context labels after a Flask request finishes."""
    _CURRENT_METHOD.set("-")
    _CURRENT_ROUTE.set("-")


def compact_sql(statement: str) -> str:
    """Normalizes SQL whitespace so it fits better in the presentation view."""
    return re.sub(r"\s+", " ", statement).strip()


def summarize_params(statement: str, params: Any) -> str:
    """Returns a readable, short parameter summary with basic password redaction."""
    if params is None:
        return "-"

    if "password" in statement.lower():
        return "[redacted password fields]"

    text = repr(params)
    if len(text) > 180:
        return f"{text[:177]}..."
    return text


def operation_name(statement: str) -> str:
    """Extracts the first SQL keyword for quick scanning."""
    sql = compact_sql(statement)
    return sql.split(" ", 1)[0].upper() if sql else "SQL"


def operation_concept(operation: str) -> str:
    """Returns a short academic label for the SQL operation."""
    labels = {
        "SELECT": "Consulta datos",
        "INSERT": "Crea registros",
        "UPDATE": "Modifica registros",
        "DELETE": "Elimina registros",
    }
    return labels.get(operation, "Ejecuta SQL")


def extract_tables(statement: str) -> list[str]:
    """Extracts likely table names from common SQL statements."""
    sql = compact_sql(statement)
    patterns = [
        r"\bFROM\s+`?([a-zA-Z_][\w]*)`?",
        r"\bJOIN\s+`?([a-zA-Z_][\w]*)`?",
        r"\bINTO\s+`?([a-zA-Z_][\w]*)`?",
        r"\bUPDATE\s+`?([a-zA-Z_][\w]*)`?",
    ]
    tables: list[str] = []
    for pattern in patterns:
        for table in re.findall(pattern, sql, flags=re.IGNORECASE):
            normalized = table.lower()
            if normalized not in tables:
                tables.append(normalized)
    return tables


def build_summary(entries: list[dict]) -> dict:
    """Aggregates trace entries into totals, errors, operations and table counts.

    Pure function: no side effects, no global state. The caller passes the list
    of entries it already has (for example, the result of
    `get_sql_trace_entries`). Useful for the live dashboard and for tests.
    """
    operations: dict[str, int] = {"SELECT": 0, "INSERT": 0, "UPDATE": 0, "DELETE": 0}
    table_counts: dict[str, int] = {}
    error_count = 0

    for entry in entries:
        if entry.get("status") == "ERROR":
            error_count += 1

        op_full = str(entry.get("operation") or "")
        op_key = op_full.split(" ", 1)[0].upper() if op_full else ""
        if op_key in operations:
            operations[op_key] += 1

        for table in entry.get("tables") or []:
            table_counts[table] = table_counts.get(table, 0) + 1

    sorted_tables = sorted(table_counts.items(), key=lambda item: (-item[1], item[0]))
    top_tables = dict(sorted_tables[:8])

    return {
        "total": len(entries),
        "errors": error_count,
        "operations": operations,
        "tables": top_tables,
    }


def build_trace_entry(
    operation: str,
    params: Any,
    status: str,
    error: str,
    duration_ms: float,
) -> dict[str, Any]:
    """Builds the trace record shown in the presentation UI."""
    op_name = operation_name(operation)
    return {
        "time": datetime.now().strftime("%H:%M:%S"),
        "method": _CURRENT_METHOD.get(),
        "route": _CURRENT_ROUTE.get(),
        "operation": op_name,
        "concept": operation_concept(op_name),
        "tables": extract_tables(operation),
        "sql": compact_sql(operation),
        "params": summarize_params(operation, params),
        "duration_ms": duration_ms,
        "status": status,
        "error": error,
    }


class TracedCursor:
    """Cursor wrapper that records calls to execute without changing CRUD code."""

    def __init__(self, cursor: Any) -> None:
        self._cursor = cursor

    def execute(self, operation: str, params: Any = None, *args: Any, **kwargs: Any) -> Any:
        started_at = time.perf_counter()
        status = "OK"
        error_message = ""

        try:
            return self._cursor.execute(operation, params, *args, **kwargs)
        except Exception as error:
            status = "ERROR"
            error_message = str(error)
            raise
        finally:
            duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
            entry = build_trace_entry(operation, params, status, error_message, duration_ms)
            _TRACE_ENTRIES.append(entry)
            print(
                f"[SQL TRACE] {entry['time']} {entry['status']} "
                f"{entry['duration_ms']}ms {entry['method']} {entry['route']} "
                f"{entry['sql']} params={entry['params']}",
                flush=True,
            )

    def executemany(self, operation: str, seq_params: Any, *args: Any, **kwargs: Any) -> Any:
        started_at = time.perf_counter()
        status = "OK"
        error_message = ""

        try:
            return self._cursor.executemany(operation, seq_params, *args, **kwargs)
        except Exception as error:
            status = "ERROR"
            error_message = str(error)
            raise
        finally:
            duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
            entry = build_trace_entry(operation, seq_params, status, error_message, duration_ms)
            entry["operation"] = f"{entry['operation']} MANY"
            _TRACE_ENTRIES.append(entry)
            print(
                f"[SQL TRACE] {entry['time']} {entry['status']} "
                f"{entry['duration_ms']}ms {entry['method']} {entry['route']} "
                f"{entry['sql']} params={entry['params']}",
                flush=True,
            )

    def __getattr__(self, name: str) -> Any:
        return getattr(self._cursor, name)


class TracedConnection:
    """Connection wrapper that returns traced cursors."""

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def cursor(self, *args: Any, **kwargs: Any) -> TracedCursor:
        return TracedCursor(self._connection.cursor(*args, **kwargs))

    def __getattr__(self, name: str) -> Any:
        return getattr(self._connection, name)
