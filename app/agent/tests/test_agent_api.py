from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.enums import AgentStatus, AgentType
from app.agent.models import Agent
from app.agent.tests.utils import create_agent

RETRIEVE_ENDPOINT = "/agents/{agent_id}"
LIST_ENDPOINT = "/agents"


class TestRetrieveAgentAPI:
    """Tests for the single-agent retrieval endpoint."""

    async def test_get_agent_success(self, client: AsyncClient, db: AsyncSession):
        data = {
            "name": "Sales-Agent",
            "type": AgentType.SALES,
            "description": "Sales-Agent-Description",
        }
        agent = await create_agent(db, **data)

        response = await client.get(RETRIEVE_ENDPOINT.format(agent_id=agent.id))
        assert response.status_code == status.HTTP_200_OK

        body = response.json()
        assert body["id"] == str(agent.id)
        for key, value in data.items():
            assert body[key] == value

    async def test_not_found(self, client: AsyncClient):
        """Unknown UUID returns 404."""
        response = await client.get(RETRIEVE_ENDPOINT.format(agent_id=uuid4()))
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
class TestListAgentsAPI:
    """Matrix of filters + error cases for the list endpoint."""

    @pytest.mark.parametrize(
        "params,expected_names",
        [
            ({}, {"Alpha Sales", "Beta Support", "Gamma Marketing", "Delta Sales"}),
            ({"q": "alpha"}, {"Alpha Sales"}),
            ({"type": AgentType.SALES.value}, {"Alpha Sales", "Delta Sales"}),
            ({"status": AgentStatus.INACTIVE.value}, {"Gamma Marketing"}),
            (
                {"q": "sales", "type": AgentType.SALES.value},
                {"Alpha Sales", "Delta Sales"},
            ),
            (
                {"type": AgentType.SALES.value, "status": AgentStatus.ACTIVE.value},
                {"Alpha Sales", "Delta Sales"},
            ),
            (
                {
                    "q": "delta",
                    "type": AgentType.SALES.value,
                    "status": AgentStatus.ACTIVE.value,
                },
                {"Delta Sales"},
            ),
        ],
    )
    async def test_list_agents_success(
        self,
        seeded_agents: list[Agent],
        client: AsyncClient,
        params: dict,
        expected_names: set[str],
    ):
        response = await client.get(LIST_ENDPOINT, params=params)
        assert response.status_code == status.HTTP_200_OK
        assert {item["name"] for item in response.json()} == expected_names

    @pytest.mark.parametrize(
        "params,bad_field",
        [
            ({"type": "Unknown"}, "type"),
            ({"status": "Sleeping"}, "status"),
        ],
    )
    async def test_invalid_enum_values(
        self, client: AsyncClient, params: dict, bad_field: str
    ):
        """Passing an enum value that isn't allowed should trigger 422."""
        response = await client.get(LIST_ENDPOINT, params=params)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        error_fields = {err["loc"][-1] for err in response.json()["detail"]}
        assert bad_field in error_fields
