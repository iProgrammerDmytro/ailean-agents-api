from enum import StrEnum


class AgentType(StrEnum):
    SALES = "Sales"
    SUPPORT = "Support"
    MARKETING = "Marketing"


class AgentStatus(StrEnum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
