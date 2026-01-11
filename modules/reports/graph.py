"""Graph helpers: build and export address graphs using networkx.

Export prefers Graphviz (pygraphviz or pydot). If not available, falls back to Matplotlib.
"""
from typing import Iterable, Dict, Any
import os

try:
    import networkx as nx
except Exception:  # pragma: no cover - tests will ensure networkx is available
    raise


def build_graph_from_edges(edges: Iterable[Dict[str, Any]]) -> nx.DiGraph:
    """Build a directed graph from edges iterable (dicts with from, to, value, tx, time)."""
    g = nx.DiGraph()
    for e in edges:
        src = e.get("from")
        dst = e.get("to")
        if not src or not dst:
            continue
        g.add_node(src)
        g.add_node(dst)
        attrs = {k: v for k, v in e.items() if k not in ("from", "to")}
        g.add_edge(src, dst, **attrs)
    return g


def export_graph_image(g: nx.DiGraph, out_path: str, fmt: str = "png") -> None:
    """Export graph to image. Tries Graphviz backends first, then matplotlib.

    Args:
        g: NetworkX DiGraph
        out_path: output file path (extension optional)
        fmt: image format (png, svg, pdf)
    """
    _, ext = os.path.splitext(out_path)
    if not ext:
        out_path = f"{out_path}.{fmt}"

    # Try pygraphviz (preferred)
    try:
        from networkx.drawing.nx_agraph import to_agraph

        A = to_agraph(g)
        A.layout(prog="dot")
        A.draw(out_path)
        return
    except Exception:
        pass

    # Try pydot
    try:
        from networkx.drawing.nx_pydot import to_pydot

        P = to_pydot(g)
        P.set_rankdir("LR")
        P.write(out_path, format=fmt)
        return
    except Exception:
        pass

    # Fallback to matplotlib
    try:
        import matplotlib.pyplot as plt

        pos = None
        try:
            # prefer graphviz layout if available
            pos = nx.nx_agraph.graphviz_layout(g, prog="dot")
        except Exception:
            pos = nx.spring_layout(g)
        plt.figure(figsize=(10, 6))
        nx.draw_networkx_nodes(g, pos, node_size=300)
        nx.draw_networkx_edges(g, pos, arrows=True)
        nx.draw_networkx_labels(g, pos, font_size=8)
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(out_path, format=fmt)
        plt.close()
        return
    except Exception as e:
        raise RuntimeError(f"Failed to export graph: {e}")
