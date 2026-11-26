# cenit

Document-specific extractor for the Banrep CENIT participants table.

The table lives on page 1 of the CENIT codes PDF. The extractor discovers the grid from PDF geometry, validates the rotated Spanish headers, and emits schema version 2 with English envelope fields and Spanish domain keys.

## Install

```bash
uv sync
```

## Usage

```bash
uv run cenit ../cenit_codes.pdf --page 1 --output /tmp/cenit
uv run cenit ../cenit_codes.pdf --source-url https://www.banrep.gov.co/sites/default/files/codigos-compensacion-cenit.pdf
```

Outputs:

- `<output>.json`: participants and totals
- `<output>_report.json`: structured validation report
- `<output>_debug.json`: geometry, labels and the raw matrix
- `<output>.csv`: flat 15-column view

## Versioned data

- `data/current/cenit.json`: committed extraction snapshot
- `data/current/cenit.csv`: flat snapshot for manual review
- `data/current/cenit_report.json`: validation report for the snapshot
- `data/current/cenit_debug.json`: geometry, labels and raw matrix
- `data/source.json`: source URL, checksum, fetch time and schema version

Report metadata, local paths and checksums are not part of the semantic comparison.

## Development

```bash
uv run python -m unittest discover -s tests
uv run cenit tests/fixtures/cenit_codes.pdf --output /tmp/ci/cenit
uv run python scripts/compare.py data/current/cenit.json /tmp/ci/cenit.json
```

## Automation

`.github/workflows/ci.yml` runs tests, compile checks and a golden-fixture extraction on pushes and pull requests.

`.github/workflows/sync-cenit.yml` runs weekly and on extractor changes. It downloads the PDF, extracts the table, compares it with `data/current/`, and opens or updates a `bot/cenit-sync` pull request only when participants or totals change. The PR is not auto-merged. Add a `GH_PAT` repository secret with `contents: write` and `pull-requests: write` permissions.
