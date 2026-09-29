from datetime import datetime, timezone
from typing import Generator

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.graph import shortest_path
from app.models import Node, Edge, RouteHistory
from app.schemas import NodeResponse, NodeCreate, EdgeResponse, EdgeCreate, RouteResponse, RouteRequest, HistoryItem

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_node(db: Session, name: str) -> Node | None:
    return db.query(Node).filter(Node.name == name).first()


@app.post("/nodes", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
def add_node(payload: NodeCreate, db: Session = Depends(get_db)):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name missing")
    if get_node(db, name):
        raise HTTPException(status_code=400, detail="Node already exists")

    node = Node(name=name)
    db.add(node)
    db.commit()
    db.refresh(node)
    return node


@app.post("/edges", response_model=EdgeResponse, status_code=status.HTTP_201_CREATED)
def add_edge(payload: EdgeCreate, db: Session = Depends(get_db)):
    source = get_node(db, payload.source)
    destination = get_node(db, payload.destination)

    if not source or not destination:
        raise HTTPException(status_code=400, detail="Source/destination nodes not found")
    if payload.source == payload.destination:
        raise HTTPException(status_code=400, detail="Source and destination must be different")

    duplicate = (
        db.query(Edge)
        .filter(
            Edge.source_id == source.id,
            Edge.destination_id == destination.id,
        )
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=400, detail="Duplicate edge")

    edge = Edge(
        source_id=source.id,
        destination_id=destination.id,
        latency=payload.latency,
    )
    db.add(edge)
    db.commit()
    db.refresh(edge)

    return EdgeResponse(
        id=edge.id,
        source=source.name,
        destination=destination.name,
        latency=edge.latency,
    )


@app.post("/routes/shortest", response_model=RouteResponse)
def get_shortest_route(payload: RouteRequest, db: Session = Depends(get_db)):
    source = get_node(db, payload.source)
    destination = get_node(db, payload.destination)

    if not source or not destination:
        raise HTTPException(status_code=400, detail="Invalid or non-existent nodes")

    nodes = db.query(Node).all()
    edges = db.query(Edge).all()
    name_by_id = {node.id: node.name for node in nodes}

    adjacency: dict[str, list[tuple[str, float]]] = {node.name: [] for node in nodes}
    for edge in edges:
        adjacency[name_by_id[edge.source_id]].append(
            (name_by_id[edge.destination_id], edge.latency)
        )

    result = shortest_path(adjacency, source.name, destination.name)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"No path exists between {source.name} and {destination.name}",
        )

    total_latency, path = result

    history = RouteHistory(
        source=source.name,
        destination=destination.name,
        total_latency=total_latency,
        path="|".join(path),
        created_at=datetime.now(timezone.utc),
    )
    db.add(history)
    db.commit()

    return RouteResponse(total_latency=total_latency, path=path)


@app.get("/routes/history", response_model=list[HistoryItem])
def get_route_history(
    source: str | None = None,
    destination: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(RouteHistory)

    if source:
        query = query.filter(RouteHistory.source == source)
    if destination:
        query = query.filter(RouteHistory.destination == destination)
    if date_from:
        query = query.filter(RouteHistory.created_at >= date_from)
    if date_to:
        query = query.filter(RouteHistory.created_at <= date_to)

    rows = query.order_by(RouteHistory.created_at.desc()).limit(limit).all()

    return [
        HistoryItem(
            id=row.id,
            source=row.source,
            destination=row.destination,
            total_latency=row.total_latency,
            path=row.path.split("|"),
            created_at=row.created_at,
        )
        for row in rows
    ]


# Nice-to-have APIs
@app.get("/nodes", response_model=list[NodeResponse])
def list_nodes(db: Session = Depends(get_db)):
    return db.query(Node).order_by(Node.id).all()


@app.get("/edges", response_model=list[EdgeResponse])
def list_edges(db: Session = Depends(get_db)):
    nodes = {n.id: n.name for n in db.query(Node).all()}
    return [
        EdgeResponse(
            id=e.id,
            source=nodes[e.source_id],
            destination=nodes[e.destination_id],
            latency=e.latency,
        )
        for e in db.query(Edge).order_by(Edge.id).all()
    ]


@app.delete("/nodes/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_node(node_id: int, db: Session = Depends(get_db)):
    node = db.get(Node, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    db.delete(node)
    db.commit()


@app.delete("/edges/{edge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_edge(edge_id: int, db: Session = Depends(get_db)):
    edge = db.get(Edge, edge_id)
    if not edge:
        raise HTTPException(status_code=404, detail="Edge not found")
    db.delete(edge)
    db.commit()
