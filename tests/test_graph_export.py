import tempfile
import os
from modules.reports.graph import build_graph_from_edges, export_graph_image


def test_graph_export_png(tmp_path):
    edges = [
        {"from": "0xA", "to": "0xB", "value": "100", "hash": "0xTX1", "time": "2020-01-01T00:00:00"},
        {"from": "0xB", "to": "0xC", "value": "200", "hash": "0xTX2", "time": "2020-01-01T01:00:00"},
    ]
    g = build_graph_from_edges(edges)
    out = tmp_path / "graph.png"
    export_graph_image(g, str(out), fmt="png")
    assert out.exists()


def test_graph_export_svg(tmp_path):
    edges = [
        {"from": "0x1", "to": "0x2", "value": "1", "hash": "0x1", "time": "2020-01"},
    ]
    g = build_graph_from_edges(edges)
    out = tmp_path / "graph.svg"
    export_graph_image(g, str(out), fmt="svg")
    assert out.exists()
