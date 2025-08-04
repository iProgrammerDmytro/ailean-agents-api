from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.enums import AgentStatus, AgentType
from app.agent.models import Agent


@pytest.fixture
async def seeded_agents(db: AsyncSession) -> list[Agent]:
    """Insert 4 agents covering all enum permutations we need."""
    agents = [
        Agent(
            id=uuid4(),
            name="Alpha Sales",
            description="Alpha sells solutions",
            type=AgentType.SALES,
        ),
        Agent(
            id=uuid4(),
            name="Beta Support",
            description="Handles support requests",
            type=AgentType.SUPPORT,
        ),
        Agent(
            id=uuid4(),
            name="Gamma Marketing",
            description="Gamma marketing efforts",
            type=AgentType.MARKETING,
            status=AgentStatus.INACTIVE,
        ),
        Agent(
            id=uuid4(),
            name="Delta Sales",
            description="Delta enterprise sales",
            type=AgentType.SALES,
        ),
    ]
    db.add_all(agents)
    await db.commit()
    return agents
