"""
Intelligent Courier Planner
Algorithms: Merge Sort, 0/1 Knapsack (Dynamic Programming), Dijkstra, Nearest-Neighbor TSP.
Run: python main.py --parcels data/parcels.csv --graph data/graph.json --capacity 25
"""
from __future__ import annotations
import argparse, csv, heapq, json, math, time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Optional

@dataclass
class Parcel:
    parcel_id: str
    destination: str
    weight: int
    priority: int
    deadline: int
    value: int

def merge_sort_parcels(items: List[Parcel]) -> List[Parcel]:
    """Stable merge sort: earliest deadline, then highest priority, then highest value."""
    if len(items) <= 1:
        return items[:]
    mid = len(items) // 2
    left, right = merge_sort_parcels(items[:mid]), merge_sort_parcels(items[mid:])
    out, i, j = [], 0, 0
    def key(p): return (p.deadline, -p.priority, -p.value, p.parcel_id)
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    return out + left[i:] + right[j:]

def knapsack_dp(parcels: List[Parcel], capacity: int):
    """0/1 knapsack. Returns selected parcels and the complete DP table."""
    n = len(parcels)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i, p in enumerate(parcels, 1):
        for cap in range(capacity + 1):
            dp[i][cap] = dp[i-1][cap]
            if p.weight <= cap:
                dp[i][cap] = max(dp[i][cap], p.value + dp[i-1][cap-p.weight])
    selected, cap = [], capacity
    for i in range(n, 0, -1):
        if dp[i][cap] != dp[i-1][cap]:
            selected.append(parcels[i-1])
            cap -= parcels[i-1].weight
    selected.reverse()
    return selected, dp

def dijkstra(graph: Dict[str, Dict[str, float]], source: str):
    dist = {node: math.inf for node in graph}
    prev = {node: None for node in graph}
    dist[source] = 0
    pq = [(0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if d != dist[u]: continue
        for v, w in graph[u].items():
            nd = d + w
            if nd < dist[v]:
                dist[v], prev[v] = nd, u
                heapq.heappush(pq, (nd, v))
    return dist, prev

def reconstruct_path(prev, start, end):
    if start == end: return [start]
    path, cur = [], end
    while cur is not None:
        path.append(cur)
        if cur == start: break
        cur = prev[cur]
    if path[-1] != start: return []
    return list(reversed(path))

def all_pairs_shortest_paths(graph):
    distances, paths = {}, {}
    for source in graph:
        dist, prev = dijkstra(graph, source)
        distances[source] = dist
        paths[source] = {target: reconstruct_path(prev, source, target) for target in graph}
    return distances, paths

def nearest_neighbor_tour(stops, distances, depot):
    """TSP approximation on the metric closure induced by shortest-path distances."""
    unvisited = set(stops) - {depot}
    route, current, total = [depot], depot, 0.0
    while unvisited:
        nxt = min(unvisited, key=lambda node: (distances[current][node], node))
        leg = distances[current][nxt]
        if math.isinf(leg): raise ValueError(f"No route from {current} to {nxt}")
        total += leg
        route.append(nxt); unvisited.remove(nxt); current = nxt
    back = distances[current][depot]
    if math.isinf(back): raise ValueError(f"No return route from {current} to depot {depot}")
    total += back
    route.append(depot)
    return route, total

def expand_tour(route, paths):
    expanded = []
    for a, b in zip(route, route[1:]):
        leg = paths[a][b]
        if not leg: raise ValueError(f"No path between {a} and {b}")
        expanded.extend(leg if not expanded else leg[1:])
    return expanded

def load_parcels(path):
    parcels = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            parcels.append(Parcel(row["parcel_id"], row["destination"], int(row["weight"]),
                                  int(row["priority"]), int(row["deadline"]), int(row["value"])))
    return parcels

def load_graph(path):
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    graph = {node: {} for node in raw["nodes"]}
    for a, b, w in raw["edges"]:
        if w < 0: raise ValueError("Dijkstra requires non-negative edge weights.")
        graph[a][b] = float(w); graph[b][a] = float(w)
    return graph, raw["depot"]

def run_planner(parcels, graph, depot, capacity):
    t0 = time.perf_counter()
    sorted_parcels = merge_sort_parcels(parcels)
    sort_ms = (time.perf_counter()-t0)*1000
    t0 = time.perf_counter()
    selected, dp = knapsack_dp(sorted_parcels, capacity)
    knapsack_ms = (time.perf_counter()-t0)*1000
    destinations = sorted(set(p.destination for p in selected))
    t0 = time.perf_counter()
    distances, paths = all_pairs_shortest_paths(graph)
    dijkstra_ms = (time.perf_counter()-t0)*1000
    t0 = time.perf_counter()
    stop_route, route_distance = nearest_neighbor_tour(destinations, distances, depot)
    expanded = expand_tour(stop_route, paths)
    tsp_ms = (time.perf_counter()-t0)*1000
    return {
        "sorted": sorted_parcels, "selected": selected, "dp": dp,
        "sort_ms": sort_ms, "knapsack_ms": knapsack_ms,
        "dijkstra_ms": dijkstra_ms, "tsp_ms": tsp_ms,
        "stop_route": stop_route, "expanded_route": expanded,
        "route_distance": route_distance,
        "total_weight": sum(p.weight for p in selected),
        "total_value": sum(p.value for p in selected),
        "destinations": destinations
    }

def print_report(result, capacity, depot):
    print("\n" + "="*64)
    print("             INTELLIGENT COURIER PLANNER")
    print("="*64)
    print(f"Depot: {depot} | Box capacity: {capacity}")
    print("\n1) PARCEL PRIORITIZATION (deadline ↑, priority ↓)")
    for p in result["sorted"]:
        print(f"  {p.parcel_id:5} -> {p.destination:8} weight={p.weight:2} "
              f"priority={p.priority} deadline={p.deadline:2} value={p.value}")
    print("\n2) OPTIMAL BOX CONTENTS (0/1 Knapsack DP)")
    for p in result["selected"]:
        print(f"  {p.parcel_id} -> {p.destination} (weight {p.weight}, value {p.value})")
    print(f"  Total weight: {result['total_weight']}/{capacity}")
    print(f"  Total value:  {result['total_value']}")
    print("\n3) DELIVERY ROUTE (Nearest Neighbor over Dijkstra distances)")
    print("  Stop sequence: " + " -> ".join(result["stop_route"]))
    print("  Road path:     " + " -> ".join(result["expanded_route"]))
    print(f"  Total route distance: {result['route_distance']:.2f} distance units")
    print("\n4) ALGORITHM RUNTIMES")
    for name, key in [("Merge sort", "sort_ms"), ("Knapsack DP", "knapsack_ms"),
                      ("All-source Dijkstra", "dijkstra_ms"), ("Nearest-neighbor TSP", "tsp_ms")]:
        print(f"  {name:25}: {result[key]:9.4f} ms")
    print("="*64)

def main():
    parser = argparse.ArgumentParser(description="Intelligent courier planning prototype")
    parser.add_argument("--parcels", default="data/parcels.csv")
    parser.add_argument("--graph", default="data/graph.json")
    parser.add_argument("--capacity", type=int, default=25)
    args = parser.parse_args()
    parcels = load_parcels(args.parcels)
    graph, depot = load_graph(args.graph)
    for p in parcels:
        if p.destination not in graph: raise ValueError(f"Unknown destination {p.destination}")
    if depot not in graph: raise ValueError(f"Unknown depot {depot}")
    result = run_planner(parcels, graph, depot, args.capacity)
    print_report(result, args.capacity, depot)

if __name__ == "__main__":
    main()
