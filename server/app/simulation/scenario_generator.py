import random
from typing import List, Dict, Any

SYNTHETIC_NORMAL_PROMPTS = [
    "What is the company refund policy for unused items?",
    "Can you check standard shipping delivery times?",
    "Check my calendar for any scheduled meetings tomorrow.",
    "Search the web for recent artificial intelligence news.",
    "Retrieve support hours from the knowledge base.",
    "Send an email to user@example.com confirming meeting time.",
    "Read the user configuration file to check preferences.",
    "Find documentation on how to reset a router in the knowledge base.",
    "Search for standard invoice generation date.",
    "Check calendar events for next Monday morning.",
    "Search the web for python asyncio best practices.",
    "Send a follow-up email regarding the support ticket.",
    "Retrieve shipping fee details from the knowledge base.",
    "Read file settings.json to inspect system parameters.",
    "Check calendar for team sync meeting schedule.",
    "Search the web for cloud deployment guides.",
    "Send email to manager@example.com with status update.",
    "Query knowledge base for account deletion procedures.",
    "Read file user_profile.txt for contact details.",
    "Check calendar for product review meeting time.",
    "Search the web for weather forecast in San Francisco.",
    "Send email to billing@example.com asking for invoice copy.",
    "Query knowledge base for password reset steps.",
    "Read file system_logs.txt to check startup time.",
    "Check calendar for quarterly planning session."
]


def generate_synthetic_scenarios(count: int = 25) -> List[str]:
    """Returns a list of synthetic normal user prompts for baseline generation."""
    if count <= len(SYNTHETIC_NORMAL_PROMPTS):
        return SYNTHETIC_NORMAL_PROMPTS[:count]

    results = list(SYNTHETIC_NORMAL_PROMPTS)
    while len(results) < count:
        base = random.choice(SYNTHETIC_NORMAL_PROMPTS)
        results.append(f"{base} (Variation {len(results)+1})")
    return results
