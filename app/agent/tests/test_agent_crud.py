from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.crud import get_agent
from app.agent.enums import AgentType
from app.agent.models import Agent
from app.agent.tests.utils import create_agent


@pytest.mark.asyncio
class TestGetAgentCRUD:
    """Unit-level validations for get_agent(db, agent_id)."""

    async def test_get_agent_success(self, db: AsyncSession):
        data = {
            "name": "Found-Me",
            "type": AgentType.MARKETING,
            "description": "Found-Me-Description",
        }
        agent = await create_agent(db, **data)

        result = await get_agent(db, agent.id)
        assert result is not None
        assert result.id == agent.id

        for key, value in data.items():
            assert getattr(result, key) == value

    async def test_returns_none_when_not_found(self, db: AsyncSession):
        """Unknown UUID should return None, not raise."""
        unknown_id = uuid4()

        result = await get_agent(db, unknown_id)

        assert result is None
