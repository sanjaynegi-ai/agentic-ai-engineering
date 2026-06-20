import logging
logger = logging.getLogger("comparison_openai_agents")
def record(kind: str, detail: str) -> None: logger.info("sdk_event", extra={"kind": kind, "detail": detail})
