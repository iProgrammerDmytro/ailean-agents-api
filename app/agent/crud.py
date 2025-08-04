from typing import Sequence
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.models import Agent
from app.agent.schemas import AgentCreate

from .enums import AgentStatus, AgentType


async def get_agents(
    db: AsyncSession,
    *,
    q: str | None = None,
    type_: AgentType | None = None,
    status: AgentStatus | None = None,
) -> Sequence[Agent]:
    stmt = select(Agent)

    if q:
        pattern = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                Agent.name.ilike(pattern),
                Agent.description.ilike(pattern),
            )
        )

    if type_:
        stmt = stmt.where(Agent.type == type_)

    if status:
        stmt = stmt.where(Agent.status == status)

    stmt = stmt.order_by(Agent.name)
    result = await db.execute(stmt)

    return result.scalars().all()


async def get_agent(db: AsyncSession, agent_id: UUID) -> Agent | None:
    result = await db.execute(select(Agent).where(Agent.id == agent_id))

    return result.scalars().first()


async def create_agent(db: AsyncSession, data: AgentCreate) -> Agent:
    agent = Agent(**data.model_dump())
    db.add(agent)

    await db.commit()
    await db.refresh(agent)

    return agent
