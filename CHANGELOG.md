# Changelog

All notable changes to **agent-ledger** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] – 2026-03-25

### Added
- `LedgerEntry` — immutable audit record with uuid4 id, timestamp, action, agent_id, details, result, error, and `to_dict()`.
- `Ledger` — in-memory audit store with `record()`, `by_agent()`, `by_action()`, `by_result()`, `since()`, `failures()`, `summary()`, and `clear()`.
- `@audit` decorator — zero-boilerplate audit wrapping with automatic success/failure recording and exception re-raise.
- Full pytest suite (30+ tests, 100% statement coverage of public API).
- Zero runtime dependencies; requires Python ≥ 3.10.
