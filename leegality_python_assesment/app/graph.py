import heapq
from typing import Iterable


def shortest_path(
    graph: dict[str, list[tuple[str, float]]],
    source: str,
    destination: str,
) -> tuple[float, list[str]] | None:
    """Dijkstra's algorithm for a directed graph with positive edge weights."""
    distances = {node: float("inf") for node in graph}
    previous: dict[str, str | None] = {node: None for node in graph}
    distances[source] = 0.0

    heap: list[tuple[float, str]] = [(0.0, source)]

    while heap:
        current_distance, current = heapq.heappop(heap)

        if current_distance > distances[current]:
            continue

        if current == destination:
            break

        for neighbor, weight in graph[current]:
            candidate = current_distance + weight
            if candidate < distances.get(neighbor, float("inf")):
                distances[neighbor] = candidate
                previous[neighbor] = current
                heapq.heappush(heap, (candidate, neighbor))

    if distances.get(destination, float("inf")) == float("inf"):
        return None

    path = []
    current: str | None = destination
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()

    return round(distances[destination], 10), path
