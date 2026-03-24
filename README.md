# agent-ledger

**Immutable audit logging and action ledger for AI agents.**

Know exactly who did what, when, and with what result — every time.

```
pip install agent-ledger
```

---

## Why

When agents take actions (file writes, API calls, data transforms) in production, you need an audit trail you can trust. Without one, debugging incidents means reconstructing history from fragmented logs. `agent-ledger` gives you:

- **Immutable entries** — each action is stamped with a uuid4 id and monotonic timestamp
- **Rich queries** — filter by agent, action type, result, or time range
- **Zero dependencies** — pure Python ≥ 3.10, nothing to install

---

## Quick Start

```python
from agent_ledger import Ledger, LedgerEntry, audit

ledger = Ledger()

# ── Manual recording ──────────────────────────────────────────────────────
ledger.record(action="read_config", agent_id="config-agent", details={"path": "/etc/app.conf"})
ledger.record(action="api_call",   agent_id="data-agent",   details={"url": "https://api.example.com/data"})
ledger.record(action="write_db",   agent_id="db-agent",     result="failure", error="connection refused")

# ── Query ─────────────────────────────────────────────────────────────────
print(ledger.by_agent("data-agent"))   # all entries for data-agent
print(ledger.failures())               # all failures
print(ledger.summary())
# {
#   "total": 3,
#   "by_result": {"success": 2, "failure": 1},
#   "by_agent": {"config-agent": 1, "data-agent": 1, "db-agent": 1}
# }
```

---

## Decorator Usage

The `@audit` decorator instruments any function automatically:

```python
from agent_ledger import Ledger, audit

ledger = Ledger()

@audit(ledger, action="transform_data", agent_id="etl-agent")
def transform(payload=None, schema=None):
    """Heavy ETL transform."""
    if payload is None:
        raise ValueError("payload is required")
    return {k: str(v) for k, v in payload.items()}


# Success path
transform(payload={"user_id": 42}, schema="v2")
# → ledger records: action="transform_data", result="success", details={"payload": ..., "schema": "v2"}

# Failure path — exception is re-raised, failure recorded
try:
    transform()
except ValueError:
    pass
# → ledger records: action="transform_data", result="failure", error="payload is required"

print(ledger.summary())
# {"total": 2, "by_result": {"success": 1, "failure": 1}, "by_agent": {"etl-agent": 2}}
```

---

## Full Agent Audit Trail Example

```python
import time
from agent_ledger import Ledger, audit

ledger = Ledger(max_entries=50_000)

# Three agents collaborate on a data pipeline
@audit(ledger, action="ingest", agent_id="ingester")
def ingest(source=None):
    return f"ingested from {source}"

@audit(ledger, action="validate", agent_id="validator")
def validate(record=None, strict=False):
    if not record:
        raise ValueError("empty record")

@audit(ledger, action="persist", agent_id="writer")
def persist(record=None, table=None):
    pass  # write to DB

# Simulate a pipeline run
ingest(source="s3://bucket/data.csv")
validate(record={"id": 1}, strict=True)
persist(record={"id": 1}, table="events")

# Simulate a bad record
try:
    validate(record=None)
except ValueError:
    pass

# Post-incident review
print(f"Total actions : {ledger.summary()['total']}")
print(f"Failures      : {len(ledger.failures())}")
for entry in ledger.failures():
    print(f"  [{entry.agent_id}] {entry.action} @ {entry.timestamp:.3f} — {entry.error}")

# Time-range query: last 60 seconds
recent = ledger.since(time.time() - 60)
print(f"Actions in last 60s: {len(recent)}")
```

Output:
```
Total actions : 4
Failures      : 1
  [validator] validate @ 1711234567.123 — empty record
Actions in last 60s: 4
```

---

## API Reference

### `LedgerEntry`

| Attribute  | Type              | Description                              |
|------------|-------------------|------------------------------------------|
| `entry_id` | `str`             | UUID4 unique identifier                  |
| `action`   | `str`             | Action name                              |
| `agent_id` | `str`             | Agent performing the action              |
| `details`  | `dict`            | Contextual key/value data                |
| `result`   | `str`             | `"success"` \| `"failure"` \| `"skipped"` |
| `error`    | `str \| None`     | Error message if result is `"failure"`   |
| `timestamp`| `float`           | Unix epoch seconds                       |

### `Ledger`

| Method / Property          | Returns               | Description                                   |
|----------------------------|-----------------------|-----------------------------------------------|
| `record(...)`              | `LedgerEntry`         | Record a new action                           |
| `entries`                  | `list[LedgerEntry]`   | Shallow copy of all entries                   |
| `by_agent(agent_id)`       | `list[LedgerEntry]`   | Filter by agent                               |
| `by_action(action)`        | `list[LedgerEntry]`   | Filter by action name                         |
| `by_result(result)`        | `list[LedgerEntry]`   | Filter by result value                        |
| `since(timestamp)`         | `list[LedgerEntry]`   | Entries at or after timestamp                 |
| `failures()`               | `list[LedgerEntry]`   | All failure entries                           |
| `summary()`                | `dict`                | Aggregate stats                               |
| `clear()`                  | `None`                | Remove all entries                            |

### `@audit(ledger, action, agent_id)`

Wraps any callable. Kwargs are captured as `details`. Re-raises exceptions unchanged.

---

## License

MIT © Darshankumar Joshi
