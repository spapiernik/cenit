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

record = cenit.get_by_code("1013")
print(record.participant_name)
print(record.operation_start_date, record.operation_start_note)
print(record.footnotes)

for variant in record.account_capabilities.savings_account_number_lengths:
    print(variant.lengths, variant.footnote_markers, variant.scope)

print(cenit.is_valid_account_number_length("1013", "savings", 10))
print(cenit.is_valid_account_number_length("1013", "savings", 5))
print(
    cenit.is_valid_account_number_length(
        "1013",
        "savings",
        5,
        scope="special_collection_agreement",
    )
)

print(cenit.list_account_number_lengths("1013", "savings", scope="standard"))
print(cenit.get_by_name("bancamia"))
print(cenit.all_records())
print(cenit.totals().entity_types.bank)
```

`get_by_code` and `get_by_name` return `None` when nothing matches; `get_by_code_or_raise` raises `KeyError`.

## Qualified account lengths

The source does not publish one flat list of digits. It publishes groups with footnote markers, and those markers change the meaning of the group. `AccountNumberLengthVariant` preserves that structure:

```python
AccountNumberLengthVariant(
    lengths=(5, 7, 13),
    footnote_markers=("**",),
    scope=AccountNumberLengthScope.SPECIAL_COLLECTION_AGREEMENT,
)
```

For BANCO BBVA, the savings account cell `(5, 7,13)**, 9, 10, 12, 14, 16` becomes two variants: `(5, 7, 13)` for special collection agreements and `(9, 10, 12, 14, 16)` for standard use. `12***` becomes one variant with scope `includes_leading_zeros`.

Use `is_valid_account_number_length` when validating a number. With the default `standard` scope, 5 is not valid for BBVA. With `special_collection_agreement`, it is.

Footnote meanings are available through `cenit.footnotes()`:

| Marker | Meaning |
|---|---|
| `(*)` | Linked before May 2025 |
| `(**)` | Used for special collection agreements |
| `(***)` | Includes leading zeros |
| `(****)` | Electronic deposit service available but not enabled in CENIT |

`operation_start_date` is a `date` when the source has a date. `operation_start_note` keeps a footnote such as `"(*)"` when the source has no date.

## Record fields

`cenit.ParticipantRecord` uses English `snake_case` names and typed values:

- `row_number`: `int`
- `participant_name`: `str`
- `cenit_code`: four-digit `str`
- `operation_start_date`: `date` or `None`
- `operation_start_note`: `str` or `None`
- `entity_types`: tuple of English values such as `"bank"` or `"information_operator"`
- `supports_debit_transactions`: `bool`
- `account_capabilities`: qualified variants for savings, checking and electronic deposit lengths
- `electronic_or_low_value_deposit_name`: `str` or `None`
- `footnotes`: tuple of official markers that apply to the row

`cenit.Code` is an alias for `ParticipantRecord`.

Public functions:

- `get_by_code(code)` and `get_by_code_or_raise(code)`
- `get_by_name(name)`
- `all_records()`
- `routing_code(code)`
- `footnotes()` and `footnote_definitions(language="en")`
- `get_account_capabilities(code)`
- `list_account_number_lengths(code, account_type, scope=None)`
- `is_valid_account_number_length(code, account_type, length, scope="standard")`
- `list_participants_by_entity_type(entity_type)`
- `list_debit_capable_participants()`
- `totals()`
- `display(value)`, `render(value)`, `explore(value)`, `save(value, path)`, `to_text(value)`, `to_html(value)` and `to_svg(value)`
- `version()`, `schema_version()`, `source_date()`, `source_url()`, `source_sha256()` and `source_fetched_at()`

The routing code is `1` followed by the three-digit participant code. `routing_code` accepts either a full CENIT code such as `"1007"` or a participant code such as `"007"`.

`totals().entity_types` is a typed object, so counts are available as attributes such as `bank` and `information_operator`.

## Viewing data

Rendering uses [Rich](https://rich.readthedocs.io/) for printable output and [Textual](https://textual.textualize.io/) for the interactive explorer. Both are installed with the package. The public data classes implement `__rich_console__`, so a single value can be printed directly. Use `cenit.display` or `cenit.render` for collections because they group values into tables automatically.

```python
import cenit

record = cenit.get_by_code("1013")
cenit.display(record)
cenit.display([record, record])
cenit.display([record, cenit.totals()])
cenit.display([record, [record, cenit.totals()]])

cenit.explore([record, cenit.totals()])
```

`cenit.explore` opens a scrollable Textual view with bordered, striped, colorized `DataTable` widgets. Press `q` to quit.

Consecutive values of the same class become rows in one table. Different classes and nested collections become separate tables with dim separator rules. Lists of scalars become cell rows, and lists of lists become matrices. Nested dataclasses are expanded into their own columns, so `Totals` shows `Participants` followed by one column per entity type instead of a compact `EntityTypeTotals(...)` string.

Column labels use the full source terminology in the selected language, for example `Código de Compensación CENIT`, `Inicio de Operación`, `Tipo de Entidad` and `Aplica Transacciones Débito`. Account data appears in four columns: `Cuenta de Ahorros`, `Cuenta Corriente`, `Depósito Electrónico o de Bajo Monto` and `Nombre del Depósito Electrónico o de Bajo Monto`. English uses the same title capitalization. Entity type values are translated as well, for example `Operador de Información` and `Information Operator`.

`Operation Start` shows the date when present and the source marker such as `(*)` when there is no date. The `Footnotes` column is hidden by default. Marker definitions are printed below the tables and are also available through `cenit.footnote_definitions("spa")`.

`View` controls the output:

```python
view = cenit.View(
    language="es",
    columns=(
        "participant_name",
        "cenit_code",
        "operation_start_date",
        "supports_debit_transactions",
        "savings_account_number_lengths",
        "checking_account_number_lengths",
        "electronic_or_low_value_deposit_number_lengths",
        "electronic_or_low_value_deposit_name",
    ),
    exclude=(),
    show_columns=True,
    show_footnotes=True,
    keep_excluded_columns=False,
    title="Participantes CENIT",
    separator=True,
    separator_style="dim",
    row_columns={1: ("cenit_code",)},
    width=160,
)
cenit.display([record, cenit.get_by_code("1070")], view=view)
```

- `language` accepts ISO 639-1 codes `en` and `es`, and ISO 639-2 codes `eng` and `spa`, case-insensitive.
- `columns` selects fields. `exclude` removes fields. `keep_excluded_columns=True` keeps removed fields as empty cells.
- `show_columns=False` hides the header row. `show_footnotes=False` hides the marker definitions below the tables.
- `row_columns` maps a zero-based row index to the fields shown for that row.
- `title`, `separator` and `separator_style` control table titles and separator rules.

Exports use Rich's console recorder:

```python
records = cenit.all_records()[:5]
text = cenit.to_text(records, language="es")
html = cenit.to_html(records, width=160)
svg = cenit.to_svg(records)

cenit.save(records, "out/cenit.txt")
cenit.save(records, "out/cenit.html", width=160)
cenit.save(records, "out/cenit.svg")
```

`save` infers the format from `.txt`, `.html` or `.svg`. `render` returns the Rich renderable when a custom console or further composition is needed.

## Data model

- `data/current/cenit.json` is the versioned, auditable source of truth and keeps the Spanish domain keys from the PDF.
- `src/cenit/_data.py` is generated from that JSON with English public names and imported by the library. There is no JSON parsing at runtime.
- `data/source.json` records the source URL, PDF checksum, official document date, fetch time and schema version.
- The package version defines the dataset snapshot.

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
