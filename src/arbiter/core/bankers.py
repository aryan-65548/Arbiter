from arbiter.core.banker_state import SlotAllocation, SlotPoolState
from arbiter.core.models import AgentClaim


def find_safe_sequence(state: SlotPoolState) -> tuple[str, ...] | None:
    """Return an agent completion order, or None if the state is unsafe."""
    work = state.available_slots
    unfinished = list(state.agents)
    sequence: list[str] = []

    while unfinished:
        for agent in unfinished:
            if agent.need_slots <= work:
                work += agent.allocated_slots
                sequence.append(agent.agent_id)
                unfinished.remove(agent)
                break
        else:
            return None

    return tuple(sequence)


def is_safe(state: SlotPoolState) -> bool:
    """Return whether all agents can finish in some order."""
    return find_safe_sequence(state) is not None


def register_agent(
    state: SlotPoolState,
    agent_id: str,
    claim: AgentClaim,
) -> SlotPoolState | None:
    """Return the updated state, or None if registration is unsafe."""
    if any(agent.agent_id == agent_id for agent in state.agents):
        raise ValueError(f"agent {agent_id!r} is already registered")

    candidate = SlotPoolState(
        total_slots=state.total_slots,
        agents=state.agents + (SlotAllocation(agent_id=agent_id, claim=claim),),
    )

    if not is_safe(candidate):
        return None

    return candidate