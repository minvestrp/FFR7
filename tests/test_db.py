import tempfile
import os
from modules.forensics.db import ForensicsDB


def test_db_init_and_insert():
    tf = tempfile.NamedTemporaryFile(delete=False)
    tf.close()
    db_path = tf.name
    try:
        db = ForensicsDB(db_path)
        db.init_tables()
        inv_id = db.add_investigation("0xABCDEF", notes="Unit test")
        assert isinstance(inv_id, int)
        edge_id = db.add_edge(inv_id, "0xA", "0xB", "100", "0xTX", "2020-01-01T00:00:00")
        assert isinstance(edge_id, int)
        res = db.get_investigation(inv_id)
        assert res["investigation"]["address"] == "0xABCDEF"
        assert len(res["edges"]) == 1
    finally:
        try:
            os.unlink(db_path)
        except Exception:
            pass
