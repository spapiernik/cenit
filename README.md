# cenit

Versioned, offline lookups for official CENIT compensation codes.

```bash
uv add cenit
```

For one-off scripts:

```bash
uv run --with cenit python script.py
```

```python
import cenit

participant = cenit.get_by_code("1013")
print(participant.name, participant.code)
print(participant.supports_account_number_length("savings", 10))
print(participant.csv())
print(cenit.EntityType.BANK in participant.entity_types)
print(cenit.get_by_name("bamlom", default=None))
print(len(cenit.all_records()))
print(cenit.source().document_date)
```

`get_by_code` and `get_by_name` raise `ParticipantNotFound` unless `default` is given; `get_by_name` uses fuzzy matching. Rendering and exports live in `cenit.view`.
