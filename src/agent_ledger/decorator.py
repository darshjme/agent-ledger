"""@audit decorator — automatically records ledger entries around function calls."""

from __future__ import annotations

import functools
from typing import Any, Callable

from .ledger import Ledger


def audit(ledger: Ledger, action: str, agent_id: str) -> Callable:
    """
    Decorator factory that records audit entries for each function call.

    Usage::

        ledger = Ledger()

        @audit(ledger, action="write_file", agent_id="file-agent")
        def write_file(path, content):
            ...

    On success  → entry recorded with result="success".
    On exception → entry recorded with result="failure", error=str(exc), re-raises.

    Keyword arguments passed to the wrapped function are captured as *details*.
    """
    if not isinstance(ledger, Ledger):
        raise TypeError("ledger must be a Ledger instance")
    if not action:
        raise ValueError("action must be a non-empty string")
    if not agent_id:
        raise ValueError("agent_id must be a non-empty string")

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            details = dict(kwargs) if kwargs else {}
            try:
                result_value = func(*args, **kwargs)
                ledger.record(
                    action=action,
                    agent_id=agent_id,
                    details=details,
                    result="success",
                )
                return result_value
            except Exception as exc:
                ledger.record(
                    action=action,
                    agent_id=agent_id,
                    details=details,
                    result="failure",
                    error=str(exc),
                )
                raise

        return wrapper

    return decorator
