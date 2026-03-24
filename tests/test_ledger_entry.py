"""Tests for LedgerEntry."""

import time
import pytest
from agent_ledger import LedgerEntry


# ──────────────────────────────────────────────────────────── construction


def test_entry_basic_fields():
    e = LedgerEntry(action="write_file", agent_id="agent-1")
    assert e.action == "write_file"
    assert e.agent_id == "agent-1"
    assert e.result == "success"
    assert e.error is None
    assert e.details == {}
    assert isinstance(e.entry_id, str) and len(e.entry_id) == 36  # uuid4
    assert isinstance(e.timestamp, float)


def test_entry_with_details():
    details = {"path": "/tmp/x", "size": 42}
    e = LedgerEntry(action="write_file", agent_id="agent-1", details=details)
    assert e.details == details


def test_entry_with_failure():
    e = LedgerEntry(
        action="api_call",
        agent_id="agent-2",
        result="failure",
        error="timeout",
    )
    assert e.result == "failure"
    assert e.error == "timeout"


def test_entry_with_skipped():
    e = LedgerEntry(action="transform", agent_id="a", result="skipped")
    assert e.result == "skipped"


def test_entry_unique_ids():
    e1 = LedgerEntry(action="a", agent_id="a")
    e2 = LedgerEntry(action="a", agent_id="a")
    assert e1.entry_id != e2.entry_id


def test_entry_timestamp_recent():
    before = time.time()
    e = LedgerEntry(action="a", agent_id="a")
    after = time.time()
    assert before <= e.timestamp <= after


def test_entry_to_dict_keys():
    e = LedgerEntry(action="x", agent_id="y", details={"k": 1}, result="failure", error="oops")
    d = e.to_dict()
    assert set(d.keys()) == {"entry_id", "action", "agent_id", "details", "result", "error", "timestamp"}


def test_entry_to_dict_values():
    e = LedgerEntry(action="do_thing", agent_id="bot-1", details={"n": 7}, result="success")
    d = e.to_dict()
    assert d["action"] == "do_thing"
    assert d["agent_id"] == "bot-1"
    assert d["details"] == {"n": 7}
    assert d["result"] == "success"
    assert d["error"] is None


def test_entry_invalid_result():
    with pytest.raises(ValueError, match="result must be one of"):
        LedgerEntry(action="a", agent_id="a", result="unknown")


def test_entry_empty_action():
    with pytest.raises(ValueError, match="action"):
        LedgerEntry(action="", agent_id="a")


def test_entry_empty_agent_id():
    with pytest.raises(ValueError, match="agent_id"):
        LedgerEntry(action="a", agent_id="")


def test_entry_repr():
    e = LedgerEntry(action="ping", agent_id="bot")
    r = repr(e)
    assert "ping" in r
    assert "bot" in r


def test_entry_details_none_becomes_empty_dict():
    e = LedgerEntry(action="a", agent_id="b", details=None)
    assert e.details == {}
