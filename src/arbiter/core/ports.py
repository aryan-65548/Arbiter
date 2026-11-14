from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    """Time source used by broker algorithms."""

    def monotonic(self) -> float:
        """Return monotonic seconds for elapsed-time calculations."""
        ...

    def utcnow(self) -> datetime:
        """Return timezone-aware UTC time for persisted timestamps."""
        ...