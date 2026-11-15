from dataclasses import dataclass

from arbiter.core.models import AgentClaim


@dataclass(frozen=True, slots=True)
class SlotAllocation:
    agent_id: str
    claim: AgentClaim
    allocated_slots: int = 0

    def __post_init__(self) -> None:
        if not self.agent_id.strip():
            raise ValueError("agent_id cannot be empty")

        if self.allocated_slots < 0:
            raise ValueError("allocated_slots cannot be negative")

        if self.allocated_slots > self.claim.max_concurrent_slots:
            raise ValueError("allocation cannot exceed the agent's claim")

    @property
    def need_slots(self) -> int:
        return self.claim.max_concurrent_slots - self.allocated_slots


@dataclass(frozen=True, slots=True)
class SlotPoolState:
    total_slots: int
    agents: tuple[SlotAllocation, ...] = ()

    def __post_init__(self) -> None:
        if self.total_slots < 1:
            raise ValueError("total_slots must be at least 1")

        agent_ids = [agent.agent_id for agent in self.agents]
        if len(agent_ids) != len(set(agent_ids)):
            raise ValueError("agent IDs must be unique within a pool")

        allocated = sum(agent.allocated_slots for agent in self.agents)
        if allocated > self.total_slots:
            raise ValueError("total allocation cannot exceed pool capacity")

    @property
    def available_slots(self) -> int:
        allocated = sum(agent.allocated_slots for agent in self.agents)
        return self.total_slots - allocated