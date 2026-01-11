import pytest
from modules.analyzer.slither_wrapper import analyze_contract_from_path


def test_analyze_nonexistent_file():
    res = analyze_contract_from_path("nonexistent.sol")
    assert "issues" in res

