from uuid import UUID

from fastapi import APIRouter, Query, status

from app.agent import crud
from app.agent.schemas import (
    AgentCreate,
    AgentRead,
    AskQuestionRequest,
    AskQuestionResponse,
)
from app.db.deps import AsyncSessionDependency
from app.exceptions import BadRequest, NotFound

from .enums import AgentStatus, AgentType
from .services.qa import answer

AGENT_NAME = "Hotel Q&A Bot"


router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("", response_model=list[AgentRead])
async def list_agents(
    db: AsyncSessionDependency,
    q: str | None = Query(None, description="Fuzzy search in name/description"),
    type: AgentType | None = Query(None),
    status: AgentStatus | None = Query(None),
) -> list[AgentRead]:
    """
    Return all agents or a filtered subset.

    - **q**: case-insensitive substring match for *name* or *description*
    - **type**: filter by agent type (Sales, Support, Marketing)
    - **status**: filter by status (Active, Inactive)
    """

    return await crud.get_agents(db, q=q, type_=type, status=status)


@router.get("/{agent_id}", response_model=AgentRead)
async def get_agent(agent_id: UUID, db: AsyncSessionDependency) -> AgentRead:
    agent = await crud.get_agent(db, agent_id)
    if not agent:
        raise NotFound("Agent not found")

    return agent


@router.post("", response_model=AgentRead, status_code=status.HTTP_201_CREATED)
async def create_agent(payload: AgentCreate, db: AsyncSessionDependency) -> AgentRead:
    return await crud.create_agent(db, payload)


@router.post("/{agent_id}/ask", response_model=AskQuestionResponse)
async def ask_hotel_bot(
    agent_id: UUID, payload: AskQuestionRequest, db: AsyncSessionDependency
) -> AskQuestionResponse:
    agent = await crud.get_agent(db, agent_id)
    if not agent:
        raise NotFound("Agent not found")

    if agent.name.lower() != AGENT_NAME.lower():
        raise BadRequest(f"Only {AGENT_NAME} can answer questions")

    return AskQuestionResponse(answer=answer(payload.question))
