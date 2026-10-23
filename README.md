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
