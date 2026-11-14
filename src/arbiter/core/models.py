from dataclasses import dataclass, field
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


def _require_nonnegative(**values: int) -> None:
    negative = [name for name, value in values.items() if value < 0]
    if negative:
        raise ValueError(f"resource amounts cannot be negative: {', '.join(negative)}")


@dataclass(frozen=True, slots=True)
class AgentClaim:
    # Banker’s algorithm uses this reusable capacity claim.
    max_concurrent_slots: int

    def __post_init__(self) -> None:
        if self.max_concurrent_slots < 1:
            raise ValueError("max_concurrent_slots must be at least 1")


@dataclass(frozen=True, slots=True)
class ConcurrencyRequest:
    # Slots are held during a call and returned when it ends.
    slots: int = 1

    def __post_init__(self) -> None:
        _require_nonnegative(slots=self.slots)


@dataclass(frozen=True, slots=True)
class ProviderRateRequest:
    # Request attempts and provider tokens are rate limited separately.
    requests: int = 1
    tokens: int = 0

    def __post_init__(self) -> None:
        _require_nonnegative(requests=self.requests, tokens=self.tokens)


@dataclass(frozen=True, slots=True)
class RunBudgetReservation:
    # Reserve the call's expected maximum; settle against actual use later.
    tokens: int = 0
    cost_microusd: int = 0

    def __post_init__(self) -> None:
        _require_nonnegative(tokens=self.tokens, cost_microusd=self.cost_microusd)


@dataclass(frozen=True, slots=True)
class ResourceRequest:
    concurrency: ConcurrencyRequest = field(default_factory=ConcurrencyRequest)
    provider_rate: ProviderRateRequest = field(default_factory=ProviderRateRequest)
    run_budget: RunBudgetReservation = field(default_factory=RunBudgetReservation)

    def __post_init__(self) -> None:
        amounts = (
            self.concurrency.slots,
            self.provider_rate.requests,
            self.provider_rate.tokens,
            self.run_budget.tokens,
            self.run_budget.cost_microusd,
        )
        if not any(amount > 0 for amount in amounts):
            raise ValueError("request must reserve at least one resource")


@dataclass(frozen=True, slots=True)
class AdmissionDecision:
    status: AdmissionStatus
    reason: DecisionReason
    wait_ms: int | None = None
    queue_position: int | None = None
    lease_id: str | None = None