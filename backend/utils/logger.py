"""
Event Logger Module
Maintains an event timeline for the simulation dashboard.
Categorizes events into INFO, SUCCESS, WARNING, and ERROR.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

class EventLevel:
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"

class SimulationLogger:
    def __init__(self, max_history: int = 150):
        self.events: List[Dict[str, Any]] = []
        self.max_history = max_history
        self._start_time = time.time()

    def log(
        self,
        message: str,
        level: str = EventLevel.INFO,
        robot_id: Optional[str] = None,
        category: str = "GENERAL",
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Record an event with simulation elapsed timestamp."""
        elapsed = time.time() - self._start_time
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)
        time_str = f"{mins:02d}:{secs:02d}"

        entry = {
            "id": len(self.events) + 1,
            "timestamp": time_str,
            "time_seconds": round(elapsed, 1),
            "level": level,
            "robot_id": robot_id,
            "category": category,
            "message": message,
            "details": details or {}
        }

        self.events.append(entry)
        if len(self.events) > self.max_history:
            self.events.pop(0)

        return entry

    def reset(self):
        self.events.clear()
        self._start_time = time.time()

    def get_recent(self, count: int = 40) -> List[Dict[str, Any]]:
        return self.events[-count:]
