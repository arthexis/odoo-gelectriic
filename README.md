# Odoo Bastion query tools

The inserted, verified Bastion key selects the Odoo instance. Neither client
has an instance name, database host, or endpoint embedded in its executable.

The key must provide encrypted active bundles under `bastion/odoo/`:

- `active.postgres.toml.enc` for `bin/odoo-query`: `ssh_target` and one
  concrete PostgreSQL `.pgpass` record.
- `active.http.toml.enc` for `bin/odoo-domain`: HTTPS Odoo URL, database,
  service login, and password.

Both use the host-local mode-0600 passphrase at
`~/.local/state/odoo/.bastion-passphrase`; secrets are never stored in this
repository. The removable mount remains read-only outside deliberate bundle
provisioning.

## Read-only PostgreSQL through the key's SSH target

```bash
bin/odoo-query --check
bin/odoo-query --sql 'SELECT 1'
```

This interface opens an SSH tunnel using the expected Bastion identity. It
accepts one guarded `SELECT` or `EXPLAIN SELECT` only and executes it in a
read-only transaction.

## Native Odoo domain queries over HTTPS

```bash
bin/odoo-domain --check
bin/odoo-domain \
  --model res.partner \
  --domain '[["customer_rank", ">", 0]]' \
  --fields id,name,customer_rank \
  --limit 10
```

`odoo-domain` uses HTTPS/XML-RPC directly—no SSH tunnel. It executes
`search_read` only and supports native Odoo domains supplied as JSON arrays.
The dedicated service account is read-only and restricted to these business
models: partners, products, sales, invoices, stock, CRM leads, and purchases.
Administrative and credential-bearing models are excluded.

## BOM materials from sales-order input

`bin/odoo-bom` reads sales-order references from CSV, TSV, JSON, or plain text
(one reference per line), expands nested manufacturing BOMs over the direct
HTTPS Odoo interface, and writes CSV. CSV headers may use `sales order`,
`sales_order`, `sale order`, `sale_order`, `order`, or `name`.

```bash
bin/odoo-bom orders.csv --output materials.csv
```

The output columns are `sales order`, `product name`, `description`, `price`,
`quantity`, `tax`, `item subtotal tax`, and `subtotal with tax`. Price is the
component list price; zero-price materials are omitted. `item subtotal tax` is
the tax amount on `price × quantity`, using the effective rate calculated on
the originating sales-order line. Files written with `--output` use UTF-8 with
a BOM so Excel recognizes accents and other non-ASCII characters correctly.
The HTTP account receives read access only to the BOM models required for this
report.
