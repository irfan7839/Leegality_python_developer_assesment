from datetime import datetime
from typing import Annotated

from pydantic import (
    Field,
    BeforeValidator,
)


def validate_node_name(value: str) -> str:
    value = value.strip()

    if not value:
        raise ValueError("node name must not be blank")

    return value


NodeName = Annotated[
    str,
    Field(min_length=1, max_length=255),
    BeforeValidator(validate_node_name),
]