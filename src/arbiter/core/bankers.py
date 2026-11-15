from arbiter.core.banker_state import SlotPoolState


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