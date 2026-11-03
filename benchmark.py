"""Repeatable synthetic benchmark; writes results/benchmark.csv and runtime_chart.png."""
import csv, random, time
from pathlib import Path
from main import Parcel, merge_sort_parcels, knapsack_dp, all_pairs_shortest_paths, nearest_neighbor_tour

random.seed(7)
sizes = [20, 50, 100, 200]
rows=[]
for n in sizes:
    parcels=[Parcel(f"P{i}", f"N{random.randint(0, max(4,n//5))}", random.randint(1,12),
                    random.randint(1,5), random.randint(1,30), random.randint(10,100)) for i in range(n)]
    t=time.perf_counter(); ordered=merge_sort_parcels(parcels); sort=(time.perf_counter()-t)*1000
    t=time.perf_counter(); knapsack_dp(ordered, 100); dp=(time.perf_counter()-t)*1000
    # Connected ring graph: all-source Dijkstra; graph size scales with number of delivery nodes.
    count=max(5, min(40, n//5))
    graph={f"N{i}":{} for i in range(count)}
    for i in range(count):
        a,b=f"N{i}",f"N{(i+1)%count}"
        graph[a][b]=1.0; graph[b][a]=1.0
        c,d=f"N{i}",f"N{(i+2)%count}"
        graph[c][d]=2.5; graph[d][c]=2.5
    t=time.perf_counter(); distances,_=all_pairs_shortest_paths(graph); dij=(time.perf_counter()-t)*1000
    stops=list(graph.keys())[1:min(count,11)]
    t=time.perf_counter(); nearest_neighbor_tour(stops,distances,"N0"); tsp=(time.perf_counter()-t)*1000
    rows.append({"parcels":n,"graph_nodes":count,"merge_sort_ms":sort,"knapsack_dp_ms":dp,
                 "all_source_dijkstra_ms":dij,"nearest_neighbor_tsp_ms":tsp})
Path("results").mkdir(exist_ok=True)
with open("results/benchmark.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
try:
    import matplotlib.pyplot as plt
    for key,label in [("merge_sort_ms","Merge sort"),("knapsack_dp_ms","Knapsack DP"),
                      ("all_source_dijkstra_ms","All-source Dijkstra"),("nearest_neighbor_tsp_ms","Nearest-neighbor TSP")]:
        plt.plot([r["parcels"] for r in rows],[r[key] for r in rows],marker="o",label=label)
    plt.xlabel("Number of parcels"); plt.ylabel("Runtime (milliseconds)")
    plt.title("Courier planner: component runtime benchmark")
    plt.grid(True,alpha=.3); plt.legend(); plt.tight_layout()
    plt.savefig("results/runtime_chart.png",dpi=160); plt.close()
except ImportError:
    print("matplotlib not installed; CSV benchmark saved, chart skipped.")
print("Benchmark complete: results/benchmark.csv")
