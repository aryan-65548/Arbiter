from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from arbiter.core.models import AdmissionStatus, DecisionReason


class APIModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AgentClaimIn(APIModel):
    max_concurrent_slots: int = Field(ge=1)


class RegisterAgentIn(APIModel):
    claim: AgentClaimIn


class RegisterAgentOut(APIModel):
    agent_id: UUID


class ConcurrencyRequestIn(APIModel):
    slots: int = Field(default=1, ge=0)


class ProviderRateRequestIn(APIModel):
    requests: int = Field(default=1, ge=0)
    tokens: int = Field(default=0, ge=0)


class RunBudgetReservationIn(APIModel):
    tokens: int = Field(default=0, ge=0)
    cost_microusd: int = Field(default=0, ge=0)


class ResourceRequestIn(APIModel):
    concurrency: ConcurrencyRequestIn = Field(default_factory=ConcurrencyRequestIn)
    provider_rate: ProviderRateRequestIn = Field(default_factory=ProviderRateRequestIn)
    run_budget: RunBudgetReservationIn = Field(default_factory=RunBudgetReservationIn)

    @model_validator(mode="after")
    def require_at_least_one_resource(self) -> "ResourceRequestIn":
        amounts = (
            self.concurrency.slots,
            self.provider_rate.requests,
            self.provider_rate.tokens,
            self.run_budget.tokens,
            self.run_budget.cost_microusd,
        )
        if not any(amount > 0 for amount in amounts):
            raise ValueError("request must reserve at least one resource")
        return self


class CreateRequestIn(APIModel):
    agent_id: UUID
    resources: ResourceRequestIn


class AdmissionResponse(APIModel):
    request_id: UUID
    status: AdmissionStatus
    reason_code: DecisionReason
    wait_ms: int | None = Field(default=None, ge=0)
    queue_position: int | None = Field(default=None, ge=1)
    lease_id: UUID | None = None
    expires_at: datetime | None = None


class ReleaseRequestIn(APIModel):
    lease_id: UUID


class HeartbeatRequestIn(APIModel):
    lease_id: UUID
