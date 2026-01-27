import sys
import os
import importlib
import tempfile

from modules.forensics.db import ForensicsDB
from modules.forensics.trace_analyzer import TraceAnalyzer


def test_cli_export_json(monkeypatch, tmp_path, capsys):
    # Prepare fake txs
    fake_txs = [
        {"from": "0xA", "to": "0xB", "value": "100", "hash": "0xTX1", "timeStamp": "1600000000"},
    ]

    ta = TraceAnalyzer(api_key="DUMMY")
    monkeypatch.setattr(ta, 'fetch_txs', lambda address, page_size=1000: fake_txs)

    # Monkeypatch TraceAnalyzer used in CLI to our instance
    import modules.forensics as mf
    monkeypatch.setattr(mf, 'TraceAnalyzer', lambda: ta)
    out_file = tmp_path / "out.json"
    sys_argv = sys.argv
    try:
        sys.argv = ['cli.py', '--address', '0xSOMEADDR', '--export', 'json', '--out', str(out_file)]
        import interface.cli as cli
        importlib.reload(cli)
        cli.main()
        captured = capsys.readouterr()
        assert 'Investigation saved with id' in captured.out
        assert out_file.exists()
    finally:
        sys.argv = sys_argv
