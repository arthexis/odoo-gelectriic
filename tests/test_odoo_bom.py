import importlib.machinery
import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "bin" / "odoo-bom"
LOADER = importlib.machinery.SourceFileLoader("odoo_bom", str(SCRIPT))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
MODULE = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(MODULE)


def test_read_order_refs_supports_csv_tsv_json_and_text(tmp_path):
    fixtures = {
        "orders.csv": "sales order,ignored\nSO001,x\nSO002,y\n",
        "orders-single-column.csv": "sales order\nSO008\n",
        "orders.tsv": "order\tignored\nSO003\tx\n",
        "orders.json": '["SO004", {"sales_order": "SO005"}]',
        "orders.txt": "SO006\nSO007\n",
    }
    for name, content in fixtures.items():
        path = tmp_path / name; path.write_text(content)
        assert MODULE.read_order_refs(path)


def test_relation_id_handles_odoo_relations():
    assert MODULE.relation_id([7, "Product"]) == 7
    assert MODULE.relation_id(9) == 9
    assert MODULE.relation_id(False) is None


def test_output_columns_match_report_contract():
    assert MODULE.OUTPUT_COLUMNS == ("sales order", "product name", "description", "price", "quantity", "tax", "subtotal with tax")
