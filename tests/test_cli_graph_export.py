import sys
import importlib
from pathlib import Path

import pytest


def test_cli_graph_export(monkeypatch, tmp_path, capsys):
    # Prepare fake TraceAnalyzer that returns edges when analyze_and_store is called
    class FakeTA:
        def __init__(self):
            pass
        def analyze_and_store(self, address, db, build_graph=False):
            # Create a small investigation in db
            inv_id = db.add_investigation(address, notes="fake")
            db.add_edge(inv_id, '0xA', '0xB', '1', '0xTX', '2020-01-01T00:00:00')
            return inv_id

    import modules.forensics as mf
    monkeypatch.setattr(mf, 'TraceAnalyzer', lambda: FakeTA())

    out_json = tmp_path / "inv.json"
    out_graph = tmp_path / "graph.png"

    sys_argv = sys.argv
    try:
        sys.argv = ['cli.py', '--address', '0xSOMEADDR', '--export', 'json', '--out', str(out_json), '--graph-out', str(out_graph)]
        import interface.cli as cli
        importlib.reload(cli)
        cli.main()
        assert out_json.exists()
        assert out_graph.exists()
    finally:
        sys.argv = sys_argv
