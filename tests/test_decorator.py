"""Tests for @audit decorator."""

import pytest
from agent_ledger import Ledger, audit


# ──────────────────────────────────────────────────────────── basic success


def test_audit_records_success():
    ledger = Ledger()

    @audit(ledger, action="compute", agent_id="calc-bot")
    def add(x, y):
        return x + y

    result = add(1, 2)
    assert result == 3
    assert len(ledger) == 1
    entry = ledger.entries[0]
    assert entry.action == "compute"
    assert entry.agent_id == "calc-bot"
    assert entry.result == "success"
    assert entry.error is None


def test_audit_captures_kwargs_as_details():
    ledger = Ledger()

    @audit(ledger, action="call_api", agent_id="api-bot")
    def fetch(url=None, timeout=30):
        return "ok"

    fetch(url="http://example.com", timeout=5)
    entry = ledger.entries[0]
    assert entry.details == {"url": "http://example.com", "timeout": 5}


def test_audit_no_kwargs_empty_details():
    ledger = Ledger()

    @audit(ledger, action="ping", agent_id="monitor")
    def ping():
        return True

    ping()
    assert ledger.entries[0].details == {}


# ──────────────────────────────────────────────────────────── failure / re-raise


def test_audit_records_failure_on_exception():
    ledger = Ledger()

    @audit(ledger, action="risky", agent_id="bot")
    def risky():
        raise RuntimeError("something broke")

    with pytest.raises(RuntimeError, match="something broke"):
        risky()

    assert len(ledger) == 1
    entry = ledger.entries[0]
    assert entry.result == "failure"
    assert entry.error == "something broke"


def test_audit_reraises_original_exception_type():
    ledger = Ledger()

    @audit(ledger, action="boom", agent_id="bot")
    def boom():
        raise ValueError("bad value")

    with pytest.raises(ValueError):
        boom()


def test_audit_multiple_calls_accumulated():
    ledger = Ledger()

    @audit(ledger, action="step", agent_id="worker")
    def step(n=0):
        if n == 2:
            raise Exception("fail at 2")
        return n

    step(n=0)
    step(n=1)
    with pytest.raises(Exception):
        step(n=2)

    assert len(ledger) == 3
    assert ledger.entries[0].result == "success"
    assert ledger.entries[1].result == "success"
    assert ledger.entries[2].result == "failure"


# ──────────────────────────────────────────────────────────── preserves function metadata


def test_audit_preserves_docstring():
    ledger = Ledger()

    @audit(ledger, action="x", agent_id="y")
    def my_func():
        """My docstring."""

    assert my_func.__doc__ == "My docstring."


def test_audit_preserves_name():
    ledger = Ledger()

    @audit(ledger, action="x", agent_id="y")
    def my_func():
        pass

    assert my_func.__name__ == "my_func"


# ──────────────────────────────────────────────────────────── validation


def test_audit_invalid_ledger():
    with pytest.raises(TypeError, match="Ledger"):
        @audit("not-a-ledger", action="x", agent_id="y")
        def f():
            pass


def test_audit_empty_action():
    ledger = Ledger()
    with pytest.raises(ValueError, match="action"):
        @audit(ledger, action="", agent_id="y")
        def f():
            pass


def test_audit_empty_agent_id():
    ledger = Ledger()
    with pytest.raises(ValueError, match="agent_id"):
        @audit(ledger, action="x", agent_id="")
        def f():
            pass


# ──────────────────────────────────────────────────────────── integration


def test_audit_with_summary():
    ledger = Ledger()

    @audit(ledger, action="transform", agent_id="etl")
    def transform(data=None):
        if data is None:
            raise ValueError("no data")
        return data.upper()

    transform(data="hello")
    transform(data="world")
    with pytest.raises(ValueError):
        transform()

    s = ledger.summary()
    assert s["total"] == 3
    assert s["by_result"]["success"] == 2
    assert s["by_result"]["failure"] == 1
    assert s["by_agent"]["etl"] == 3
