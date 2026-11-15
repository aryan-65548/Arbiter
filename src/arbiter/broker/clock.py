from datetime import UTC, datetime
from time import monotonic

from arbiter.core.ports import Clock


class SystemClock(Clock):
    """Production clock implementation."""

    def monotonic(self) -> float:
        return monotonic()

    def utcnow(self) -> datetime:
        return datetime.now(UTC)
