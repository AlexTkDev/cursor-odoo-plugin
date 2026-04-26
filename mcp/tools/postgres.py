"""PostgreSQL introspection tools for Odoo databases."""

from __future__ import annotations

import os
from collections.abc import Iterable
from typing import Any

from .common import error_result, tool_result


def _connect(dsn: str | None = None) -> Any:
    try:
        import psycopg
        from psycopg.rows import dict_row
    except ImportError as exc:  # pragma: no cover - depends on optional package
        raise RuntimeError("Install psycopg to use PostgreSQL tools: pip install 'psycopg[binary]>=3.1'") from exc

    resolved_dsn = dsn or os.environ.get("ODOO_DB_DSN") or os.environ.get("DATABASE_URL")
    if not resolved_dsn:
        raise ValueError("Provide dsn or set ODOO_DB_DSN/DATABASE_URL")
    return psycopg.connect(resolved_dsn, row_factory=dict_row)


def _fetch_all(query: str, params: Iterable[Any] = (), dsn: str | None = None) -> list[dict[str, Any]]:
    with _connect(dsn) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, tuple(params))
            return list(cursor.fetchall())


def db_list_models(dsn: str | None = None) -> dict[str, Any]:
    """List Odoo models from ``ir_model``."""

    try:
        rows = _fetch_all(
            """
            SELECT model, name, state, transient
              FROM ir_model
             ORDER BY model
            """,
            dsn=dsn,
        )
    except Exception as exc:  # noqa: BLE001 - tool returns structured errors
        return error_result("db_connection_or_query_failed", str(exc))

    return tool_result(True, data={"models": rows, "count": len(rows)})


def db_describe_model(model: str, dsn: str | None = None) -> dict[str, Any]:
    """Describe an Odoo model using registry metadata and physical columns."""

    try:
        model_rows = _fetch_all(
            """
            SELECT id, model, name, state, transient
              FROM ir_model
             WHERE model = %s
            """,
            [model],
            dsn=dsn,
        )
        if not model_rows:
            return error_result("model_not_found", f"Model not found in ir_model: {model}", model=model)

        fields = _fetch_all(
            """
            SELECT name, field_description, ttype, relation, required, readonly, store, index
              FROM ir_model_fields
             WHERE model = %s
             ORDER BY name
            """,
            [model],
            dsn=dsn,
        )
        table_name = model.replace(".", "_")
        columns = _fetch_all(
            """
            SELECT column_name, data_type, is_nullable, column_default
              FROM information_schema.columns
             WHERE table_schema = 'public'
               AND table_name = %s
             ORDER BY ordinal_position
            """,
            [table_name],
            dsn=dsn,
        )
        indexes = _fetch_all(
            """
            SELECT indexname, indexdef
              FROM pg_indexes
             WHERE schemaname = 'public'
               AND tablename = %s
             ORDER BY indexname
            """,
            [table_name],
            dsn=dsn,
        )
    except Exception as exc:  # noqa: BLE001
        return error_result("db_connection_or_query_failed", str(exc), model=model)

    warnings = []
    if not columns:
        warnings.append(
            {
                "code": "physical_table_not_found",
                "message": "No physical PostgreSQL table was found; this may be an abstract, SQL-view, or transient model.",
                "table": table_name,
            }
        )

    return tool_result(
        True,
        warnings=warnings,
        metadata={"model": model, "table": table_name},
        data={"model": model_rows[0], "fields": fields, "columns": columns, "indexes": indexes},
    )


def db_missing_indexes(dsn: str | None = None, min_seq_scan: int = 1000) -> dict[str, Any]:
    """Find Odoo tables with heavy sequential scans and few/no index scans."""

    try:
        rows = _fetch_all(
            """
            SELECT relname AS table,
                   seq_scan,
                   idx_scan,
                   n_live_tup,
                   CASE
                     WHEN idx_scan = 0 THEN NULL
                     ELSE round(seq_scan::numeric / idx_scan, 2)
                   END AS seq_to_idx_ratio
              FROM pg_stat_user_tables
             WHERE seq_scan >= %s
               AND n_live_tup > 0
             ORDER BY seq_scan DESC, n_live_tup DESC
             LIMIT 100
            """,
            [min_seq_scan],
            dsn=dsn,
        )
    except Exception as exc:  # noqa: BLE001
        return error_result("db_connection_or_query_failed", str(exc), min_seq_scan=min_seq_scan)

    warnings = [
        {
            "code": "index_candidate",
            "message": "High sequential scan count detected; inspect common Odoo domains before adding an index.",
            "table": row["table"],
            "seq_scan": row["seq_scan"],
            "idx_scan": row["idx_scan"],
        }
        for row in rows
    ]
    return tool_result(True, warnings=warnings, metadata={"min_seq_scan": min_seq_scan}, data={"candidates": rows})
