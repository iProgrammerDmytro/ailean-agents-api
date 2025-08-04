from typing import Annotated

from pydantic import Field

NameStr = Annotated[
    str,
    Field(
        min_length=1,
        max_length=100,
        strip_whitespace=True,
        description="Human-readable agent name (1-100 chars)",
    ),
]

QuestionStr = Annotated[
    str,
    Field(
        min_length=1,
        max_length=300,
        strip_whitespace=True,
        description="Question to ask the agent (1-300 chars)",
    ),
]
