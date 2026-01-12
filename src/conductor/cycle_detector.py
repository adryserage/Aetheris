"""
Cycle Detector for Aetheris Conductor (v3.0)

Detects infinite loops during execution by tracking state hashes.
"""

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class ExecutionState:
    """Represents execution state at a point in time"""

    step_id: str
    step_number: int
    arguments: Dict[str, Any]
    previous_outputs: Dict[str, Any]

    def compute_hash(self) -> str:
        """Compute hash of this state for cycle detection"""
        state_data = {
            "step_id": self.step_id,
            "arguments": self.arguments,
            "outputs": self.previous_outputs,
        }
        # Use JSON serialization for consistent hashing
        state_str = json.dumps(state_data, sort_keys=True, default=str)
        return hashlib.sha256(state_str.encode()).hexdigest()[:16]


@dataclass
class CycleDetector:
    """Detects infinite loops during plan execution"""

    max_repetitions: int = 2
    _seen_states: Set[str] = field(default_factory=set)
    _state_counts: Dict[str, int] = field(default_factory=dict)
    _state_history: List[ExecutionState] = field(default_factory=list)

    def check_state(self, state: ExecutionState) -> bool:
        """
        Check if this state indicates a cycle.

        Returns True if a cycle is detected, False otherwise.
        """
        state_hash = state.compute_hash()
        self._state_history.append(state)

        # Track how many times we've seen this state
        self._state_counts[state_hash] = self._state_counts.get(state_hash, 0) + 1
        count = self._state_counts[state_hash]

        if count > self.max_repetitions:
            return True

        self._seen_states.add(state_hash)
        return False

    def reset(self) -> None:
        """Reset the detector for a new execution"""
        self._seen_states.clear()
        self._state_counts.clear()
        self._state_history.clear()

    def get_cycle_info(self) -> Optional[Dict[str, Any]]:
        """Get information about detected cycle, if any"""
        for state_hash, count in self._state_counts.items():
            if count > self.max_repetitions:
                # Find the states that caused the cycle
                cycle_states = [s for s in self._state_history if s.compute_hash() == state_hash]
                if cycle_states:
                    return {
                        "detected": True,
                        "state_hash": state_hash,
                        "repetition_count": count,
                        "step_id": cycle_states[0].step_id,
                        "first_occurrence": cycle_states[0].step_number,
                        "last_occurrence": cycle_states[-1].step_number,
                    }

        return None

    def get_history_length(self) -> int:
        """Get number of states tracked"""
        return len(self._state_history)

    def get_unique_states(self) -> int:
        """Get number of unique states seen"""
        return len(self._seen_states)


def detect_output_loop(
    outputs: List[Any],
    window_size: int = 3,
) -> bool:
    """
    Detect if outputs are looping (same sequence repeating).

    Args:
        outputs: List of outputs to check
        window_size: Size of the window to check for repetition

    Returns:
        True if a loop is detected
    """
    if len(outputs) < window_size * 2:
        return False

    # Check if the last window_size outputs match a previous window
    recent = outputs[-window_size:]

    # Look for the same sequence earlier in the outputs
    for i in range(len(outputs) - window_size * 2, -1, -1):
        window = outputs[i : i + window_size]
        if _outputs_equal(window, recent):
            return True

    return False


def _outputs_equal(a: List[Any], b: List[Any]) -> bool:
    """Check if two output lists are equal"""
    if len(a) != len(b):
        return False

    for x, y in zip(a, b):
        try:
            if json.dumps(x, sort_keys=True, default=str) != json.dumps(
                y, sort_keys=True, default=str
            ):
                return False
        except (TypeError, ValueError):
            if x != y:
                return False

    return True
