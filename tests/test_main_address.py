import sys
import importlib
from types import SimpleNamespace

import pytest


def test_main_fetches_contract_and_runs_analysis(monkeypatch, capsys):
    # Ensure fresh import
    if 'main' in sys.modules:
        importlib.reload(sys.modules['main'])

    # Monkeypatch fetch_contract_source to return simple source
    def fake_fetch(address, api_key=None):
        return 'pragma solidity ^0.8.0; contract T { function f() public { tx.origin; } }'

    # Monkeypatch analyze_contract_from_path to return deterministic issues
    def fake_analyze(path):
        return {"issues": [{"pattern": "tx.origin", "message": "Found pattern tx.origin"}], "raw": None}

    monkeypatch.setattr('modules.extractors.etherscan_fetcher.fetch_contract_source', fake_fetch)
    monkeypatch.setattr('modules.analyzer.analyze_contract_from_path', fake_analyze)

    sys_argv = sys.argv
    try:
        sys.argv = ['main.py', '--contract', '0x1111111111111111111111111111111111111111']
        import main
        main.main()
        captured = capsys.readouterr()
        assert 'Contract Analysis' in captured.out
        assert 'tx.origin' in captured.out
    finally:
        sys.argv = sys_argv
