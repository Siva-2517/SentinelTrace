import math
from typing import Dict, Any, List
import numpy as np

SENSITIVE_KEYWORDS = [
    "external", "attacker", "evil", "exfiltrate", "admin",
    "override", "secret", "password", "api_key", "system_prompt",
    "malicious", "hidden", "ignore", "relay"
]


def calculate_entropy(text: str) -> float:
    """Calculate Shannon entropy of a string (measures randomness/encoding complexity)."""
    if not text:
        return 0.0
    prob_dict = {}
    for char in text:
        prob_dict[char] = prob_dict.get(char, 0) + 1
    entropy = 0.0
    total = len(text)
    for count in prob_dict.values():
        p = count / total
        entropy -= p * math.log2(p)
    return float(entropy)


def extract_turn_features(tool_calls: List[Dict[str, Any]]) -> List[float]:
    """
    Transforms turn event tool call data into a fixed 12-dimensional numeric feature vector:
    [
        0: total_tool_calls,
        1: calls_kb_retriever,
        2: calls_send_email,
        3: calls_web_search,
        4: calls_read_file,
        5: calls_calendar,
        6: avg_param_length,
        7: avg_param_entropy,
        8: total_response_length,
        9: avg_step_latency_ms,
        10: suspicious_transition_flag, (e.g. retriever -> send_email)
        11: sensitive_keyword_density
    ]
    """
    if not tool_calls:
        # Default feature vector for turn with zero tool calls
        return [0.0] * 12

    total_calls = float(len(tool_calls))
    tool_names = [tc.get("tool", "") for tc in tool_calls]

    kb_count = float("knowledge_base_retriever" in tool_names)
    email_count = float("send_email" in tool_names)
    search_count = float("web_search" in tool_names)
    file_count = float("read_file" in tool_names)
    cal_count = float("calendar_query" in tool_names)

    param_lengths = []
    param_entropies = []
    response_lengths = []
    latencies = []
    sensitive_matches = 0

    for tc in tool_calls:
        params_str = str(tc.get("params", {}))
        param_lengths.append(len(params_str))
        param_entropies.append(calculate_entropy(params_str))
        response_lengths.append(float(tc.get("response_length", 0)))
        latencies.append(float(tc.get("latency_ms", 0.0)))

        params_lower = params_str.lower()
        for kw in SENSITIVE_KEYWORDS:
            if kw in params_lower:
                sensitive_matches += 1

    avg_param_len = float(np.mean(param_lengths)) if param_lengths else 0.0
    avg_param_ent = float(np.mean(param_entropies)) if param_entropies else 0.0
    tot_resp_len = float(np.sum(response_lengths))
    avg_lat = float(np.mean(latencies)) if latencies else 0.0

    # Detect suspicious transition (e.g. retriever -> send_email or retriever -> search with exfil)
    suspicious_transition = 0.0
    if len(tool_names) >= 2:
        for i in range(len(tool_names) - 1):
            curr, nxt = tool_names[i], tool_names[i + 1]
            if curr == "knowledge_base_retriever" and nxt in ["send_email", "web_search", "read_file"]:
                suspicious_transition = 1.0
                break

    keyword_density = float(sensitive_matches / max(1.0, total_calls))

    feature_vector = [
        total_calls,
        kb_count,
        email_count,
        search_count,
        file_count,
        cal_count,
        avg_param_len,
        avg_param_ent,
        tot_resp_len,
        avg_lat,
        suspicious_transition,
        keyword_density
    ]

    return feature_vector


FEATURE_NAMES = [
    "total_tool_calls",
    "calls_kb_retriever",
    "calls_send_email",
    "calls_web_search",
    "calls_read_file",
    "calls_calendar",
    "avg_param_length",
    "avg_param_entropy",
    "total_response_length",
    "avg_step_latency_ms",
    "suspicious_transition_flag",
    "sensitive_keyword_density"
]
