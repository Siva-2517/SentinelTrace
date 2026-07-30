from typing import Dict
from app.config import settings


class SessionSuspicionAccumulator:
    """Tracks and updates session-level suspicion scores using exponential decay."""

    def __init__(self, decay_factor: float = settings.SUSPICION_DECAY_FACTOR):
        self.decay_factor = decay_factor

    def calculate_next_score(self, current_accumulator: float, turn_combined_score: float) -> float:
        """
        Calculates updated suspicion score for turn t:
        S_t = (decay_factor * S_{t-1}) + combined_score_t
        """
        updated_score = (self.decay_factor * current_accumulator) + turn_combined_score
        return round(float(updated_score), 4)


suspicion_accumulator_instance = SessionSuspicionAccumulator()
