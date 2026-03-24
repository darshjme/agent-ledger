"""Ledger — stores and queries audit entries."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .entry import LedgerEntry


class Ledger:
    """Immutable audit ledger for agent actions."""

    def __init__(self, max_entries: int = 10000) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be >= 1")
        self._max_entries = max_entries
        self._entries: list[LedgerEntry] = []

    # ------------------------------------------------------------------ write

    def record(
        self,
        action: str,
        agent_id: str,
        details: dict[str, Any] | None = None,
        result: str = "success",
        error: str | None = None,
    ) -> LedgerEntry:
        """Create and store a new LedgerEntry, evicting oldest if at capacity."""
        entry = LedgerEntry(
            action=action,
            agent_id=agent_id,
            details=details,
            result=result,
            error=error,
        )
        if len(self._entries) >= self._max_entries:
            self._entries.pop(0)
        self._entries.append(entry)
        return entry

    def clear(self) -> None:
        """Remove all entries from the ledger."""
        self._entries.clear()

    # ------------------------------------------------------------------- read

    @property
    def entries(self) -> list[LedgerEntry]:
        """Return a shallow copy of all entries (oldest first)."""
        return list(self._entries)

    def by_agent(self, agent_id: str) -> list[LedgerEntry]:
        """Return entries recorded for the given agent_id."""
        return [e for e in self._entries if e.agent_id == agent_id]

    def by_action(self, action: str) -> list[LedgerEntry]:
        """Return entries matching the given action name."""
        return [e for e in self._entries if e.action == action]

    def by_result(self, result: str) -> list[LedgerEntry]:
        """Return entries with the given result value."""
        return [e for e in self._entries if e.result == result]

    def since(self, timestamp: float) -> list[LedgerEntry]:
        """Return entries recorded at or after *timestamp* (epoch seconds)."""
        return [e for e in self._entries if e.timestamp >= timestamp]

    def failures(self) -> list[LedgerEntry]:
        """Convenience method: return all failure entries."""
        return self.by_result("failure")

    def summary(self) -> dict[str, Any]:
        """
        Return aggregate statistics.

        Shape::

            {
                "total": int,
                "by_result": {"success": N, "failure": N, "skipped": N, ...},
                "by_agent":  {"agent_id": N, ...},
            }
        """
        by_result: Counter[str] = Counter()
        by_agent: Counter[str] = Counter()
        for e in self._entries:
            by_result[e.result] += 1
            by_agent[e.agent_id] += 1
        return {
            "total": len(self._entries),
            "by_result": dict(by_result),
            "by_agent": dict(by_agent),
        }

    def __len__(self) -> int:
        return len(self._entries)

    def __repr__(self) -> str:
        return f"Ledger(entries={len(self._entries)}, max={self._max_entries})"
