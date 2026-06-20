class AgentError(Exception): pass
class GuardrailError(AgentError): pass
class UnknownToolError(AgentError): pass
class AgentLimitError(AgentError): pass
