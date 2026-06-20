from dataclasses import dataclass, field
@dataclass
class ConversationMemory:
    messages: list[dict[str, str]] = field(default_factory=list)
    def add(self, role: str, content: str) -> None: self.messages.append({"role": role, "content": content})
    def recent(self, limit: int = 12) -> list[dict[str, str]]: return self.messages[-limit:]
