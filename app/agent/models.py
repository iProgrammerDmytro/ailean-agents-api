import uuid

from sqlalchemy import Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.agent.enums import AgentStatus, AgentType
from app.db.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    type: Mapped[AgentType] = mapped_column(
        Enum(AgentType, name="agent_type", validate_strings=True), nullable=False
    )
    status: Mapped[AgentStatus] = mapped_column(
        Enum(AgentStatus, name="agent_status", validate_strings=True),
        nullable=False,
        default=AgentStatus.ACTIVE,
    )

    description: Mapped[str | None]
