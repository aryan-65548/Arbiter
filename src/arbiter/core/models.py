from dataclasses import dataclass
from enum import StrEnum

class AdmissionStatus(StrEnum):
    GRANTED = "granted"
    QUEUED = "queued"
    DENIED = "denied"
class DecisionReason(StrEnum):
    GRANTED = "granted"
    CAPACITY_BUSY = "capacity_busy"
    UNSAFE_STATE = "unsafe_state"
    OVER_CLAIM = "over_claim"
    RATE_LIMITED = "rate_limited"
    BUDGET_EXCEEDED = "budget_exceeded"

@dataclass(frozen=True, slots=True)
class AgentClaim:
    # Banker’s algorithm will use this reusable resource limit.
    max_concurrent_slots: int
    def _post_init_(self) -> None:
        if self.max_concurrent_slots < 1:
            raise ValueError("max_concurrent_slots must be at least 1")

@dataclass(frozen=True, slots=True)
class ResourceRequest:
    # The number of concurrent slots requested by the agent.
    concurrent_slots: int = 1
    provider_requests: int = 1
    provider_tokens: int = 0
    budget_microusd: int = 0
    def _post_init_(self) -> None:
        amounts = (
            self.concurrent_slots,
            self.provider_requests,
            self.provider_tokens,
            self.budget_microusd,
        )

        if any(amount < 0 for amount in amounts):
            raise ValueError("resource amounts cannot be negative")

        if not any(amount > 0 for amount in amounts):
            raise ValueError("request must reserve at least one resource")

@dataclass(frozen=True, slots=True)
class AdmissionDecision:
    status: AdmissionStatus
    reason: DecisionReason
    wait_ms: int | None = None
    queue_position: int | None = None
    lease_id: str | None = None