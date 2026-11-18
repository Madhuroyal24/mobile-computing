"""B3: Exhaustive renderer configuration search vs an adaptive heuristic."""
from itertools import product

QUALITIES = [("LOW", 1), ("MEDIUM", 2), ("HIGH", 3)]
CACHES = [1, 2, 3]

def cost(n_items, quality, cache, profile):
    # Transparent teaching model: lower is better; values are simulated units.
    q_penalty = (3-quality) * n_items * profile["visual_weight"]
    frame_penalty = max(0, quality*n_items - profile["frame_capacity"]) * 1.8
    energy = quality*n_items*0.45 + cache*profile["cache_energy"]
    memory_penalty = max(0, cache-profile["cache_limit"]) * 5
    return round(q_penalty + frame_penalty + energy + memory_penalty, 2)

def exact(n, profile):
    best = None; evaluated = 0
    for (qname, q), cache in product(QUALITIES, CACHES):
        evaluated += 1
        c = cost(n, q, cache, profile)
        if best is None or c < best[0]:
            best = (c, qname, cache)
    return best, evaluated

def adaptive(n, profile):
    # Starts at medium/small; raises quality only if capacity permits.
    qname, q = "MEDIUM", 2
    cache = 1
    changes = evictions = 0
    if q*n > profile["frame_capacity"]:
        qname, q = "LOW", 1
        changes += 1
    elif (q+1)*n <= profile["frame_capacity"] and profile["battery"] >= 40:
        qname, q = "HIGH", 3
        changes += 1
    target_cache = min(3, profile["cache_limit"])
    if target_cache < cache:
        evictions += cache-target_cache
        cache = target_cache
    elif target_cache > cache and profile["battery"] >= 35:
        cache = target_cache
        changes += 1
    return (cost(n, q, cache, profile), qname, cache), changes, evictions

if __name__ == "__main__":
    print("B3 – EXACT vs ADAPTIVE FEED RENDERER")
    cases = [
        ("CASE 1", 4, {"frame_capacity":12,"cache_limit":2,"battery":80,"visual_weight":1.0,"cache_energy":0.8}),
        ("CASE 2", 7, {"frame_capacity":15,"cache_limit":2,"battery":65,"visual_weight":1.2,"cache_energy":0.8}),
        ("CASE 3", 5, {"frame_capacity":5,"cache_limit":1,"battery":20,"visual_weight":0.7,"cache_energy":0.8}),
        ("COUNTEREXAMPLE", 6, {"frame_capacity":18,"cache_limit":3,"battery":25,"visual_weight":2.0,"cache_energy":0.4}),
    ]
    for name, n, p in cases:
        e, count = exact(n,p)
        a, changes, evictions = adaptive(n,p)
        print(f"\n{name}: items={n}, profile={p}")
        print(f"EXACT: cost={e[0]}, quality={e[1]}, cache={e[2]}, configurations_evaluated={count}")
        print(f"ADAPTIVE: cost={a[0]}, quality={a[1]}, cache={a[2]}, quality/cache_changes={changes}, evictions={evictions}")
        print(f"MATCH={abs(e[0]-a[0]) < 1e-9}")
    print("\nSCALABILITY")
    for n in (5, 20, 100, 500):
        _, count = exact(n, {"frame_capacity":1000,"cache_limit":3,"battery":80,"visual_weight":1.0,"cache_energy":0.8})
        _, changes, evictions = adaptive(n, {"frame_capacity":1000,"cache_limit":3,"battery":80,"visual_weight":1.0,"cache_energy":0.8})
        print(f"items={n}: exact_configurations={count}, adaptive_decisions={1+changes+evictions}")
    print("\nNote: This is a deterministic simulation cost model, not a measurement from a physical phone.")
