# Network Route Optimization API

A FastAPI service for the Network Route Optimization exercise. It provides endpoints for managing network nodes and edges, finding the shortest route, and viewing previous route requests.

## Implemented APIs

### Required

- `POST /nodes` — create a node
- `POST /edges` — create a directed edge
- `POST /routes/shortest` — find the shortest route between two nodes
- `GET /routes/history` — view route history

### Additional

- `GET /nodes` — list available nodes
- `GET /edges` — list available edges
- `DELETE /nodes/{id}` — remove a node
- `DELETE /edges/{id}` — remove an edge

The application uses SQLite with SQLAlchemy to store the data. Dijkstra's algorithm is used to calculate the shortest route.

## Design

```text
Client
  |
  v
FastAPI
  |
  +--> Pydantic validation
  |
  +--> SQLAlchemy / SQLite
  |       +--> nodes
  |       +--> edges
  |       +--> route_history
  |
  +--> Dijkstra shortest-path engine
```

Since latency values must be positive, Dijkstra's algorithm can be used to find the minimum-latency path. With `V` nodes and `E` edges, the heap-based implementation has a time complexity of `O((V + E) log V)`.

## Setup

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the API

Start the development server with:

```bash
uvicorn app.main:app --reload
```

The Swagger UI is available at:

```text
http://127.0.0.1:8000/docs
```

The SQLite database is created automatically as `routes.db` when the application starts.

## Example

### Create nodes

```bash
curl -X POST http://127.0.0.1:8000/nodes   -H "Content-Type: application/json"   -d '{"name":"ServerA"}'

curl -X POST http://127.0.0.1:8000/nodes   -H "Content-Type: application/json"   -d '{"name":"ServerB"}'

curl -X POST http://127.0.0.1:8000/nodes   -H "Content-Type: application/json"   -d '{"name":"ServerD"}'
```

### Create edges

The examples below create a path from `ServerA` to `ServerD` through `ServerB`.

```bash
curl -X POST http://127.0.0.1:8000/edges   -H "Content-Type: application/json"   -d '{"source":"ServerA","destination":"ServerB","latency":12.5}'

curl -X POST http://127.0.0.1:8000/edges   -H "Content-Type: application/json"   -d '{"source":"ServerB","destination":"ServerD","latency":10.9}'
```

### Find the shortest route

```bash
curl -X POST http://127.0.0.1:8000/routes/shortest   -H "Content-Type: application/json"   -d '{"source":"ServerA","destination":"ServerD"}'
```

Expected response:

```json
{
  "total_latency": 23.4,
  "path": ["ServerA", "ServerB", "ServerD"]
}
```

## Testing

Run the test suite with:

```bash
pytest -q
```

## Error handling

The API handles the following cases:

- Empty or missing node names → validation error / 400
- Attempting to create a duplicate node → 400
- Source or destination node does not exist → 400
- Zero or negative latency → validation error
- Attempting to create a duplicate directed edge → 400
- Invalid nodes supplied for a route request → 400
- No path between the requested nodes → 404

## Assumptions

The exercise does not specify a particular database or whether the network should be directed or undirected.

This implementation treats edges as directed, meaning an edge is stored as `source -> destination`. This follows the API format, which provides separate `source` and `destination` fields.

If the network is intended to be undirected, the graph construction can be changed to add the reverse connection as well.
