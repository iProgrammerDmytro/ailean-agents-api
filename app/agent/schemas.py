from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.agent.enums import AgentStatus, AgentType
from app.agent.types import NameStr, QuestionStr


class AgentBase(BaseModel):
    name: NameStr
    type: AgentType
    status: AgentStatus = AgentStatus.ACTIVE
    description: Optional[str] = None


class AgentCreate(AgentBase):
    pass


class AgentRead(AgentBase):
    id: UUID

    model_config = {"from_attributes": True}


class AskQuestionRequest(BaseModel):
    question: QuestionStr


class AskQuestionResponse(BaseModel):
    answer: str
