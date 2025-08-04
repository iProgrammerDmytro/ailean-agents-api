from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.enums import AgentType
from app.agent.models import Agent


async def create_agent(db: AsyncSession, **kwargs) -> Agent:
    """Synchronous helper for quick inline records (returns committed Agent)."""
    payload = dict(
        id=uuid4(),
        name="Test-Agent",
        type=AgentType.SALES,
        description="Test-Agent-Description",
    )
    payload.update(kwargs)
    agent = Agent(**payload)
    db.add(agent)
    await db.commit()

    return agent
