import pytest
from modules.forensics.trace_analyzer import TraceAnalyzer


def test_missing_api_key_raises():
    # explicitly pass None to simulate missing key
    with pytest.raises(ValueError):
        TraceAnalyzer(api_key=None)
