"""Tests for Ledger."""

import time
import pytest
from agent_ledger import Ledger, LedgerEntry


# ──────────────────────────────────────────────────────────── init


def test_ledger_default_max():
    ledger = Ledger()
    assert len(ledger) == 0


def test_ledger_invalid_max():
    with pytest.raises(ValueError):
        Ledger(max_entries=0)


def test_ledger_repr():
    ledger = Ledger(max_entries=50)
    assert "50" in repr(ledger)


# ──────────────────────────────────────────────────────────── record


def test_record_returns_entry():
    ledger = Ledger()
    entry = ledger.record(action="api_call", agent_id="bot-1")
    assert isinstance(entry, LedgerEntry)
    assert entry.action == "api_call"
    assert entry.agent_id == "bot-1"


def test_record_increments_length():
    ledger = Ledger()
    ledger.record("a", "x")
    ledger.record("b", "x")
    assert len(ledger) == 2


def test_record_with_all_fields():
    ledger = Ledger()
    entry = ledger.record(
        action="write",
        agent_id="file-agent",
        details={"path": "/tmp/f"},
        result="failure",
        error="permission denied",
    )
    assert entry.result == "failure"
    assert entry.error == "permission denied"
    assert entry.details == {"path": "/tmp/f"}


def test_record_evicts_oldest_when_full():
    ledger = Ledger(max_entries=3)
    for i in range(3):
        ledger.record(action=f"a{i}", agent_id="x")
    first_id = ledger.entries[0].entry_id
    ledger.record(action="overflow", agent_id="x")
    assert len(ledger) == 3
    assert ledger.entries[0].entry_id != first_id
    assert ledger.entries[-1].action == "overflow"


# ──────────────────────────────────────────────────────────── entries property


def test_entries_returns_copy():
    ledger = Ledger()
    ledger.record("a", "x")
    copy1 = ledger.entries
    copy2 = ledger.entries
    assert copy1 is not copy2
    copy1.clear()
    assert len(ledger) == 1


# ──────────────────────────────────────────────────────────── queries


def test_by_agent():
    ledger = Ledger()
    ledger.record("a", "agent-1")
    ledger.record("b", "agent-2")
    ledger.record("c", "agent-1")
    results = ledger.by_agent("agent-1")
    assert len(results) == 2
    assert all(e.agent_id == "agent-1" for e in results)


def test_by_agent_empty():
    ledger = Ledger()
    assert ledger.by_agent("ghost") == []


def test_by_action():
    ledger = Ledger()
    ledger.record("write", "a1")
    ledger.record("read", "a1")
    ledger.record("write", "a2")
    results = ledger.by_action("write")
    assert len(results) == 2
    assert all(e.action == "write" for e in results)


def test_by_result_success():
    ledger = Ledger()
    ledger.record("a", "x", result="success")
    ledger.record("b", "x", result="failure")
    results = ledger.by_result("success")
    assert len(results) == 1
    assert results[0].result == "success"


def test_by_result_skipped():
    ledger = Ledger()
    ledger.record("a", "x", result="skipped")
    assert len(ledger.by_result("skipped")) == 1


def test_failures():
    ledger = Ledger()
    ledger.record("a", "x", result="success")
    ledger.record("b", "x", result="failure", error="boom")
    ledger.record("c", "x", result="failure", error="crash")
    fs = ledger.failures()
    assert len(fs) == 2
    assert all(e.result == "failure" for e in fs)


def test_since():
    ledger = Ledger()
    before = time.time()
    time.sleep(0.01)
    ledger.record("a", "x")
    time.sleep(0.01)
    mid = time.time()
    time.sleep(0.01)
    ledger.record("b", "x")

    all_results = ledger.since(before)
    assert len(all_results) == 2

    after_mid = ledger.since(mid)
    assert len(after_mid) == 1
    assert after_mid[0].action == "b"


def test_since_future_returns_empty():
    ledger = Ledger()
    ledger.record("a", "x")
    assert ledger.since(time.time() + 9999) == []


# ──────────────────────────────────────────────────────────── summary


def test_summary_empty():
    ledger = Ledger()
    s = ledger.summary()
    assert s["total"] == 0
    assert s["by_result"] == {}
    assert s["by_agent"] == {}


def test_summary_counts():
    ledger = Ledger()
    ledger.record("a", "bot-1", result="success")
    ledger.record("b", "bot-1", result="success")
    ledger.record("c", "bot-2", result="failure")
    s = ledger.summary()
    assert s["total"] == 3
    assert s["by_result"]["success"] == 2
    assert s["by_result"]["failure"] == 1
    assert s["by_agent"]["bot-1"] == 2
    assert s["by_agent"]["bot-2"] == 1


# ──────────────────────────────────────────────────────────── clear


def test_clear():
    ledger = Ledger()
    ledger.record("a", "x")
    ledger.record("b", "x")
    ledger.clear()
    assert len(ledger) == 0
    assert ledger.entries == []
