# Final Project Report — Intelligent Courier Planner

## 1. Objective
Develop an integrated Python prototype that prioritizes parcels, fills a limited-capacity delivery box, computes shortest road paths, approximates a delivery tour, and measures algorithm runtimes.

## 2. Implementation
The application is implemented in `main.py`. It uses a stable merge sort, a tabular 0/1 knapsack dynamic program, heap-based Dijkstra, and nearest-neighbor TSP approximation over shortest-path distances.

## 3. Sample demonstration
Run:

```bash
python main.py --parcels data/parcels.csv --graph data/graph.json --capacity 25
```

The application prints:
- sorted parcels (earliest deadline first, then priority and value);
- selected parcels, total weight, and total value;
- ordered destination stops and expanded road path;
- route distance and measured runtime of each component.

The exact route and timings are generated on the machine used for the demonstration. Use `screenshots/sample_output.txt` as a captured sample trace.

## 4. Performance testing
Run `python benchmark.py`. It generates a CSV and a runtime chart for parcel counts 20, 50, 100, and 200. The graph size is scaled with the test size up to 40 nodes. Because the benchmark is synthetic and hardware-dependent, report measured values from the CSV rather than treating one run as universal.

Expected trends:
- Merge sort grows approximately as `n log n`.
- Knapsack DP grows with both parcel count and capacity (`nW`).
- All-source Dijkstra grows with graph size and edge count.
- Nearest-neighbor grows approximately quadratically in number of delivery stops.

## 5. Correctness and validation
- Knapsack never selects a parcel set whose total weight exceeds capacity.
- Every selected destination appears in the route once as a stop.
- Dijkstra uses non-negative weights and calculates exact shortest paths on the supplied graph.
- The route begins and ends at the depot.
- The route distance is the sum of shortest-path legs in the approximate stop order.

## 6. Improvements
Introduce delivery time windows, parcel expiration, multidimensional capacity, one-way roads, live traffic, multiple vehicles, and route improvement (2-opt). For larger graphs, avoid all-source Dijkstra by running it only from the depot and selected destinations.

## 7. Conclusion
The prototype demonstrates how sorting, dynamic programming, graph algorithms, and approximation techniques can be integrated into a single logistics workflow. It provides reproducible sample data, execution commands, and a benchmark script suitable for a lab demonstration.
