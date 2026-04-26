"""PostgreSQL introspection placeholders."""

from __future__ import annotations

from typing import Any

from .common import not_implemented


def db_list_models() -> dict[str, Any]:
    return not_implemented(
        "db_list_models",
        "Database introspection is planned for V2 and requires explicit connection policy.",
    )


def db_describe_model(model: str) -> dict[str, Any]:
    return not_implemented(
        "db_describe_model",
        "Database model description is planned for V2 and requires explicit connection policy.",
        model=model,
    )


def db_missing_indexes() -> dict[str, Any]:
    return not_implemented(
        "db_missing_indexes",
        "Missing index analysis is planned for V2 and requires explicit database access.",
    )
