import logging
from .schemas import AgentEvent
logger = logging.getLogger("comparison_agent")
def record(event: AgentEvent) -> None: logger.info("agent_event", extra={"agent_event": event.model_dump(mode="json")})
