# cenit

Versioned Python library for reading the official CENIT compensation codes.

Each release bundles one immutable snapshot of the Banrep participants table. The data is compiled into the package, so lookups are offline, deterministic and free of runtime network calls, caches or background processes. Publishing a new package version is how new data is released.

## Install

This package exposes a Python API, not a command line tool. Add it as a dependency:

```bash
uv add git+https://github.com/spapiernik/cenit.git
```

With pip:

```bash
pip install git+https://github.com/spapiernik/cenit.git
```

## Usage

```python
import cenit

record = cenit.get("1007")
if record is not None:
    print(record.cenit_code)
    print(record.participant)
    print(record.entity_types)
    print(record.operation_start_date)
    print(record.supports_debit_transactions)
    print(record.account_types.savings_account_lengths)
    print(record.electronic_or_low_value_deposit)

same_record = cenit.get(1007)
required = cenit.get_or_raise("1007")
match = cenit.find_by_name("bancamia")
records = cenit.all()

print(record.participant_code, record.routing_code)
print(cenit.routing_code("007"))
print(cenit.totals().participants)
print(cenit.version(), cenit.source_date())
```

`find_by_name` is accent-insensitive and accepts an exact name or a unique partial name. `get` returns `None` for an unknown code; `get_or_raise` raises `KeyError`.

Public functions:

- `get(code)` and `get_or_raise(code)`, keyed by the four-digit `cenit_code`
- `find_by_name(name)`
- `all()` and `all_codes()`
- `routing_code(code)`
- `totals()`
- `version()`, `schema_version()`, `source_date()`, `source_url()`, `source_sha256()` and `source_fetched_at()`

The routing code is `1` followed by the three-digit participant code. `routing_code` accepts either a full CENIT code such as `"1007"` or a participant code such as `"007"`.

## Record fields

Each `cenit.Code` uses English `snake_case` names and typed values:

- `participant`: `str`
- `cenit_code`: four-digit `str`
- `operation_start_date`: `date` or `None` when the source has a footnote instead of a date
- `operation_start_label`: original source label, such as `"(*)"` or `"3/07/2025"`
- `entity_types`: tuple of English values such as `"bank"`, `"information_operator"` or `"seped"`
- `supports_debit_transactions`: `bool`
- `account_types.savings_account_lengths`: tuple of `int`
- `account_types.checking_account_lengths`: tuple of `int`
- `electronic_or_low_value_deposit`: provider name as `str` or `None`
- `electronic_or_low_value_deposit_lengths`: tuple of `int`

`cenit.ENTITY_TYPES` lists all supported entity type values in document order.

## Data model

- `data/current/cenit.json` is the versioned, auditable source of truth and keeps the Spanish domain keys from the PDF.
- `src/cenit/_data.py` is generated from that JSON with English public names and imported by the library. There is no JSON parsing at runtime.
- `data/source.json` records the source URL, PDF checksum, official document date, fetch time and schema version.
- The package version defines the dataset snapshot, following the same model as locale data libraries that ship one deterministic release.

## Development

```bash
uv sync
uv run python -m unittest discover -s tests
uv run python scripts/generate_data.py --check
```

To refresh the bundled data from a downloaded PDF:

```bash
uv run python scripts/extract.py cenit_codes.pdf \
  --source-url https://www.banrep.gov.co/sites/default/files/codigos-compensacion-cenit.pdf \
  --output data/current/cenit
uv run python scripts/generate_data.py
```

`scripts/extract.py` and `scripts/generate_data.py` are maintenance tools. They are not part of the installed package API.

## Automation

`.github/workflows/ci.yml` runs tests, compile checks, generated-data verification and a golden-fixture extraction on pushes and pull requests.

`.github/workflows/sync-cenit.yml` runs weekly and on extractor changes. It downloads the PDF, extracts the table, compares it with `data/current/`, regenerates the compiled module and opens or updates a `bot/cenit-sync` pull request only when participants or totals change. The PR is not auto-merged. Add a `GH_PAT` repository secret with `contents: write` and `pull-requests: write` permissions.
