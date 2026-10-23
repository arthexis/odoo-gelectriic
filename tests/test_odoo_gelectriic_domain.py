import importlib.machinery
import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "bin" / "odoo-domain"
LOADER = importlib.machinery.SourceFileLoader("odoo_domain", str(SCRIPT))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
MODULE = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(MODULE)


def test_parse_domain_preserves_native_domain_shape():
    assert MODULE.parse_domain('[["customer_rank", ">", 0], ["active", "=", true]]') == [
        ["customer_rank", ">", 0], ["active", "=", True]
    ]


def test_parse_domain_rejects_non_array():
    try:
        MODULE.parse_domain('{"field": "name"}')
    except MODULE.DomainQueryError:
        pass
    else:
        raise AssertionError("non-array domain unexpectedly accepted")


def test_parse_fields_and_model_allowlist():
    assert MODULE.parse_fields("id,name,customer_rank") == ["id", "name", "customer_rank"]
    assert "res.partner" in MODULE.READABLE_MODELS
    assert "res.users" not in MODULE.READABLE_MODELS
