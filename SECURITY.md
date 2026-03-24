# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅ Yes    |

## Reporting a Vulnerability

**Please do not open public GitHub issues for security vulnerabilities.**

Email **darshjme@gmail.com** with the subject line `[SECURITY] agent-ledger` and include:

1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if any)

You will receive an acknowledgement within 48 hours and a fix timeline within 7 days.

## Scope

- `LedgerEntry`, `Ledger`, `audit` decorator — any data-exposure or integrity issues
- Dependency chain (currently zero runtime deps — scope is minimal)

## Out of Scope

- Vulnerabilities in Python itself or the standard library
- Denial-of-service via extremely large `max_entries` (by design; caller controls this)
