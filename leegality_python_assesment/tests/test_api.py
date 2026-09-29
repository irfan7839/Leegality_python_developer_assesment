from pathlib import Path
import tempfile

import pytest
from fastapi.testclient import TestClient

# Use a temporary working directory so tests do not touch the development DB.
@pytest.fixture()
def client(monkeypatch):
    import app.main as main

    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
        )
        SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        main.Base.metadata.create_all(bind=engine)

        monkeypatch.setattr(main, "engine", engine)
        monkeypatch.setattr(main, "SessionLocal", SessionLocal)

        with TestClient(main.app) as test_client:
            yield test_client


def test_add_node(client):
    response = client.post("/nodes", json={"name": "ServerA"})
    assert response.status_code == 201
    assert response.json()["name"] == "ServerA"


def test_duplicate_node(client):
    client.post("/nodes", json={"name": "ServerA"})
    response = client.post("/nodes", json={"name": "ServerA"})
    assert response.status_code == 400


def test_shortest_route_and_history(client):
    for name in ["ServerA", "ServerB", "ServerC", "ServerD"]:
        assert client.post("/nodes", json={"name": name}).status_code == 201

    edges = [
        ("ServerA", "ServerB", 12.5),
        ("ServerB", "ServerD", 10.9),
        ("ServerA", "ServerC", 30.0),
        ("ServerC", "ServerD", 2.0),
    ]
    for source, destination, latency in edges:
        assert client.post(
            "/edges",
            json={"source": source, "destination": destination, "latency": latency},
        ).status_code == 201

    response = client.post(
        "/routes/shortest",
        json={"source": "ServerA", "destination": "ServerD"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "total_latency": 23.4,
        "path": ["ServerA", "ServerB", "ServerD"],
    }

    history = client.get("/routes/history")
    assert history.status_code == 200
    assert len(history.json()) == 1
    assert history.json()[0]["path"] == ["ServerA", "ServerB", "ServerD"]


def test_no_path(client):
    client.post("/nodes", json={"name": "ServerA"})
    client.post("/nodes", json={"name": "ServerB"})

    response = client.post(
        "/routes/shortest",
        json={"source": "ServerA", "destination": "ServerB"},
    )
    assert response.status_code == 404
    assert "No path exists" in response.json()["detail"]


def test_invalid_latency(client):
    client.post("/nodes", json={"name": "ServerA"})
    client.post("/nodes", json={"name": "ServerB"})

    response = client.post(
        "/edges",
        json={"source": "ServerA", "destination": "ServerB", "latency": 0},
    )
    assert response.status_code == 422


def test_history_filters(client):
    for name in ["ServerA", "ServerB", "ServerC"]:
        client.post("/nodes", json={"name": name})

    client.post(
        "/edges",
        json={"source": "ServerA", "destination": "ServerB", "latency": 5},
    )
    client.post(
        "/routes/shortest",
        json={"source": "ServerA", "destination": "ServerB"},
    )

    response = client.get("/routes/history", params={"source": "ServerA", "limit": 1})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["source"] == "ServerA"
