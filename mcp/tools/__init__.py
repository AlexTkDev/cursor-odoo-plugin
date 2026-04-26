"""Tool registry for cursor-odoo-dev MCP server."""

from .manifest import validate_manifest
from .migration import analyze_migration
from .oca import check_oca_compliance
from .postgres import db_describe_model, db_list_models, db_missing_indexes
from .profiler import profile_module
from .scaffold import create_module
from .shell import odoo_shell_eval
from .tests import run_odoo_tests
from .xml import review_xml

__all__ = [
    "analyze_migration",
    "check_oca_compliance",
    "create_module",
    "db_describe_model",
    "db_list_models",
    "db_missing_indexes",
    "odoo_shell_eval",
    "profile_module",
    "review_xml",
    "run_odoo_tests",
    "validate_manifest",
]
