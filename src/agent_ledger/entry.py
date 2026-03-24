"""LedgerEntry — a single audited action."""

from __future__ import annotations

import time
import uuid
from typing import Any


class LedgerEntry:
    """Represents a single audited action taken by an agent."""

    VALID_RESULTS = frozenset({"success", "failure", "skipped"})

    def __init__(
        self,
        action: str,
        agent_id: str,
        details: dict[str, Any] | None = None,
        result: str = "success",
        error: str | None = None,
    ) -> None:
        if not action:
            raise ValueError("action must be a non-empty string")
        if not agent_id:
            raise ValueError("agent_id must be a non-empty string")
        if result not in self.VALID_RESULTS:
            raise ValueError(f"result must be one of {sorted(self.VALID_RESULTS)}")

        self.entry_id: str = str(uuid.uuid4())
        self.action: str = action
        self.agent_id: str = agent_id
        self.details: dict[str, Any] = details or {}
        self.result: str = result
        self.error: str | None = error
        self.timestamp: float = time.time()

    def to_dict(self) -> dict[str, Any]:
        """Serialize entry to a plain dictionary."""
        return {
            "entry_id": self.entry_id,
            "action": self.action,
            "agent_id": self.agent_id,
            "details": self.details,
            "result": self.result,
            "error": self.error,
            "timestamp": self.timestamp,
        }

    def __repr__(self) -> str:
        return (
            f"LedgerEntry(entry_id={self.entry_id!r}, action={self.action!r}, "
            f"agent_id={self.agent_id!r}, result={self.result!r}, "
            f"timestamp={self.timestamp})"
        )
