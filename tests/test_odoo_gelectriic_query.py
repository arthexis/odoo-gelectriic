import importlib.machinery
import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "bin" / "odoo-query"
LOADER = importlib.machinery.SourceFileLoader("odoo_query", str(SCRIPT))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
MODULE = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(MODULE)


def test_split_pgpass_handles_escaped_colon():
    assert MODULE.split_pgpass(r"db.example:5432:odoo:reader:pass\:word") == (
        "db.example", "5432", "odoo", "reader", "pass:word",
    )


def test_escape_pgpass_escapes_a_password_for_a_local_tunnel_record():
    assert MODULE.escape_pgpass("pass:word") == "pass\\:word"


def test_parse_pgpass_rejects_wildcard_targeting():
    try:
        MODULE.split_pgpass("db.example:5432:*:reader:password")
    except MODULE.QueryError:
        pass
    else:
        raise AssertionError("wildcard credential record unexpectedly accepted")


def test_validate_sql_allows_select_and_explain():
    assert MODULE.validate_sql("SELECT id FROM res_partner LIMIT 1;") == "SELECT id FROM res_partner LIMIT 1"
    assert MODULE.validate_sql("EXPLAIN SELECT 1") == "EXPLAIN SELECT 1"


def test_validate_sql_rejects_mutation_and_multiple_statements():
    for query in ("DELETE FROM res_partner", "SELECT 1; DELETE FROM res_partner", "SELECT pg_terminate_backend(1)"):
        try:
            MODULE.validate_sql(query)
        except MODULE.QueryError:
            pass
        else:
            raise AssertionError(f"query unexpectedly accepted: {query}")
