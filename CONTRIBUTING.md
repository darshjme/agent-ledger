# Contributing to agent-ledger

Thank you for your interest in contributing!

## Getting Started

```bash
git clone https://github.com/darshjme-codes/agent-ledger.git
cd agent-ledger
python -m pip install -e ".[dev]"
python -m pytest tests/ -v
```

## Guidelines

- **Style:** PEP 8. Use `black` and `ruff` for formatting/linting.
- **Tests:** All new features require tests. Run `pytest --cov=agent_ledger` before opening a PR.
- **Docs:** Update `README.md` and `CHANGELOG.md` for user-visible changes.
- **Commits:** Use [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, etc.).
- **Branches:** Feature branches off `main`; open a PR when ready.
- **No breaking changes** without a major version bump and prior discussion in an issue.

## Reporting Bugs

Open a GitHub issue with a minimal reproducible example, Python version, and OS.

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
