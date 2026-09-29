from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from app.database import Base


class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )


class Edge(Base):
    __tablename__ = "edges"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    source_id: Mapped[int] = mapped_column(
        ForeignKey("nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    destination_id: Mapped[int] = mapped_column(
        ForeignKey("nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    latency: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    __table_args__ = (
            UniqueConstraint(
                "source_id",
                "destination_id",
                name="uq_edge_source_destination",
            ),
            CheckConstraint(
                "latency > 0",
                name="ck_edge_latency_positive",
            ),
        )

class RouteHistory(Base):
    __tablename__ = "route_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    source: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )

    destination: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )

    total_latency: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    path: Mapped[str] = mapped_column(
        String(4000),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )