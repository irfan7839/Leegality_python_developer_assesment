from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.validation import NodeName


class NodeCreate(BaseModel):
    name: NodeName


class NodeResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class EdgeCreate(BaseModel):
    source: NodeName
    destination: NodeName
    latency: float = Field(gt=0)


class EdgeResponse(BaseModel):
    id: int
    source: str
    destination: str
    latency: float


class RouteRequest(BaseModel):
    source: NodeName
    destination: NodeName


class RouteResponse(BaseModel):
    total_latency: float
    path: list[str]


class HistoryItem(BaseModel):
    id: int
    source: str
    destination: str
    total_latency: float
    path: list[str]
    created_at: datetime

# class NodeCreate(BaseModel):
#     name: str = Field(..., min_length=1, max_length=255)
#
#     @field_validator("name")
#     @classmethod
#     def validate_name(cls, value: str) -> str:
#         value = value.strip()
#         if not value:
#             raise ValueError("name must not be blank")
#         return value
#
#
# class NodeResponse(BaseModel):
#     id: int
#     name: str
#     model_config = ConfigDict(from_attributes=True)
#
#
# class EdgeCreate(BaseModel):
#     source: str = Field(..., min_length=1, max_length=255)
#     destination: str = Field(..., min_length=1, max_length=255)
#     latency: float = Field(..., gt=0)
#
#     @field_validator("source", "destination")
#     @classmethod
#     def validate_node_name(cls, value: str) -> str:
#         value = value.strip()
#         if not value:
#             raise ValueError("node name must not be blank")
#         return value
#
#
# class EdgeResponse(BaseModel):
#     id: int
#     source: str
#     destination: str
#     latency: float
#
#
# class RouteRequest(BaseModel):
#     source: str = Field(..., min_length=1, max_length=255)
#     destination: str = Field(..., min_length=1, max_length=255)
#
#     @field_validator("source", "destination")
#     @classmethod
#     def validate_node_name(cls, value: str) -> str:
#         value = value.strip()
#         if not value:
#             raise ValueError("node name must not be blank")
#         return value
#
#
# class RouteResponse(BaseModel):
#     total_latency: float
#     path: list[str]
#
#
# class HistoryItem(BaseModel):
#     id: int
#     source: str
#     destination: str
#     total_latency: float
#     path: list[str]
#     created_at: datetime
