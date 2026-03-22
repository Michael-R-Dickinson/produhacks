from pydantic import BaseModel, Field
from enum import Enum
from time import time
from uuid import uuid4


class AgentStatus(str, Enum):
    IDLE = "idle"
    WORKING = "working"
    DONE = "done"
    ERROR = "error"


class MessageDirection(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"


class EventType(str, Enum):
    AGENT_STATUS = "agent.status"
    AGENT_THOUGHT = "agent.thought"
    AGENT_MESSAGE = "agent.message"
    REPORT_CHUNK = "report.chunk"
    REPORT_COMPLETE = "report.complete"
    CHAT_RESPONSE = "chat.response"


# -- Payload models --

class AgentStatusPayload(BaseModel):
    status: AgentStatus
    message: str = ""


class AgentThoughtPayload(BaseModel):
    text: str


class AgentMessagePayload(BaseModel):
    from_agent: str = Field(serialization_alias="from")
    to_agent: str = Field(serialization_alias="to")
    title: str
    description: str = ""
    direction: MessageDirection


class ReportChunkPayload(BaseModel):
    content: str
    section: str
    final: bool = False


class ReportCompletePayload(BaseModel):
    markdown: str
    charts: list[dict] = []


class ChatResponsePayload(BaseModel):
    text: str
    final: bool = False


# -- Envelope --

class SSEEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: float = Field(default_factory=time)
    agent_id: str
    event_type: EventType
    payload: dict

    @classmethod
    def agent_status(cls, agent_id: str, status: AgentStatus, message: str = "") -> "SSEEvent":
        p = AgentStatusPayload(status=status, message=message)
        return cls(agent_id=agent_id, event_type=EventType.AGENT_STATUS, payload=p.model_dump())

    @classmethod
    def agent_thought(cls, agent_id: str, text: str) -> "SSEEvent":
        p = AgentThoughtPayload(text=text)
        return cls(agent_id=agent_id, event_type=EventType.AGENT_THOUGHT, payload=p.model_dump())

    @classmethod
    def agent_message(
        cls,
        agent_id: str,
        from_agent: str,
        to_agent: str,
        title: str,
        description: str = "",
        direction: MessageDirection = MessageDirection.REQUEST,
    ) -> "SSEEvent":
        p = AgentMessagePayload(
            from_agent=from_agent,
            to_agent=to_agent,
            title=title,
            description=description,
            direction=direction,
        )
        return cls(agent_id=agent_id, event_type=EventType.AGENT_MESSAGE, payload=p.model_dump(by_alias=True))

    @classmethod
    def report_chunk(cls, content: str, section: str, final: bool = False) -> "SSEEvent":
        p = ReportChunkPayload(content=content, section=section, final=final)
        return cls(agent_id="orchestrator", event_type=EventType.REPORT_CHUNK, payload=p.model_dump())

    @classmethod
    def report_complete(cls, markdown: str, charts: list[dict] | None = None) -> "SSEEvent":
        p = ReportCompletePayload(markdown=markdown, charts=charts or [])
        return cls(agent_id="orchestrator", event_type=EventType.REPORT_COMPLETE, payload=p.model_dump())

    @classmethod
    def chat_response(cls, text: str, final: bool = False) -> "SSEEvent":
        p = ChatResponsePayload(text=text, final=final)
        return cls(agent_id="orchestrator", event_type=EventType.CHAT_RESPONSE, payload=p.model_dump())
