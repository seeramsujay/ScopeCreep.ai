import json
import os
import subprocess
import sys
import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "ai_watchdog_brain"))
from benchmark import validate_response

def test_validate_response_valid():
    valid_resp = {
        "alert_id": "alt_123",
        "is_scope_creep": True,
        "severity": "HIGH",
        "flagged_action": "Adding payment gateway",
        "prd_violation": "Out of scope for sprint 14",
        "recommendation": "Postpone to next quarter"
    }
    is_valid, errors = validate_response(valid_resp)
    assert is_valid is True
    assert len(errors) == 0

def test_validate_response_missing_key():
    invalid_resp = {
        "is_scope_creep": False,
        "severity": "NONE",
        "flagged_action": "None",
        "prd_violation": "None",
        "recommendation": "Proceed"
    }
    is_valid, errors = validate_response(invalid_resp)
    assert is_valid is False
    assert any("alert_id" in err for err in errors)

def test_validate_response_invalid_severity():
    invalid_resp = {
        "alert_id": "alt_456",
        "is_scope_creep": True,
        "severity": "CRITICAL",  # Not in {"HIGH", "MEDIUM", "LOW", "NONE"}
        "flagged_action": "Foo",
        "prd_violation": "Bar",
        "recommendation": "Baz"
    }
    is_valid, errors = validate_response(invalid_resp)
    assert is_valid is False
    assert any("Invalid severity" in err for err in errors)

def test_dataset_integrity():
    dataset_path = os.path.join(REPO_ROOT, "ai_watchdog_brain", "test_dataset.json")
    with open(dataset_path, "r", encoding="utf-8") as f:
        cases = json.load(f)
    assert len(cases) > 0
    for case in cases:
        assert "id" in case
        assert "type" in case
        assert "prdContext" in case
        assert "chatInput" in case
        assert "is_scope_creep" in case["expected"]
        assert "severity" in case["expected"]

def test_backend_syntax():
    server_path = os.path.join(REPO_ROOT, "backend", "server.js")
    res = subprocess.run(["node", "-c", server_path], capture_output=True, text=True)
    assert res.returncode == 0
