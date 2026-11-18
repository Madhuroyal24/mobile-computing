"""B4: Practical video encoding heuristic and a counter-example."""
DEVICES = [
    {"name":"Entry phone","cpu":"LOW","battery":22,"network_mbps":1.5,"clip_seconds":20},
    {"name":"Mid-range phone","cpu":"MID","battery":55,"network_mbps":4.0,"clip_seconds":20},
    {"name":"Flagship phone","cpu":"HIGH","battery":85,"network_mbps":12.0,"clip_seconds":20},
    {"name":"Fast Wi-Fi, low battery","cpu":"HIGH","battery":16,"network_mbps":30.0,"clip_seconds":20},
]

def choose(d):
    # Rule: low battery or weak CPU -> 480p; adequate CPU/network/battery -> 1080p; else 720p.
    if d["battery"] < 20 or d["cpu"] == "LOW" or d["network_mbps"] < 2:
        resolution, bitrate = "480p", 1.0
    elif d["cpu"] == "HIGH" and d["battery"] >= 40 and d["network_mbps"] >= 8:
        resolution, bitrate = "1080p", 4.0
    else:
        resolution, bitrate = "720p", 2.0
    size_mb = bitrate * d["clip_seconds"] / 8
    upload_s = size_mb * 8 / d["network_mbps"]
    encode_s = {"LOW": 14, "MID": 8, "HIGH": 4}[d["cpu"]] * (bitrate/2)
    # Relative illustrative energy units, not hardware battery measurements.
    energy = round(encode_s*0.08 + upload_s*0.025 + bitrate*0.3, 2)
    remaining = round(max(0, d["battery"] - energy*0.12), 2)
    return resolution, bitrate, round(size_mb,2), round(encode_s+upload_s,2), energy, remaining

if __name__ == "__main__":
    print("B4 – MULTIMEDIA ENCODING DECISION")
    for d in DEVICES:
        r = choose(d)
        print(f"\nDEVICE: {d['name']} | CPU={d['cpu']} | battery={d['battery']}% | network={d['network_mbps']} Mbps")
        print(f"SELECTED: {r[0]}, {r[1]} Mbps, upload={'NOW' if d['battery']>=20 else 'DEFER / CHARGE FIRST'}")
        print(f"ESTIMATED: file={r[2]} MB, encode+upload={r[3]} s, energy_index={r[4]}, remaining_battery_est={r[5]}%")
    print("\nCHALLENGE INPUT")
    print("Fast Wi-Fi + flagship CPU + 16% battery: the rule selects 480p because low battery is a hard constraint.")
    print("A rule based only on CPU/network would choose 1080p and could consume too much energy.")
    print("\nDECISION NOTE")
    print("Use this bounded heuristic for quick on-device decisions; it does not guarantee global minimum energy.")
    print("Exhaustive search is suitable for offline tuning of a small device-profile set, not per-upload decisions at scale.")
    print("Monitor encode time, upload completion, battery change, thermal state, bitrate, frame drops and failures.")
    print("\nNote: Energy and battery values are illustrative model estimates, not measured phone telemetry.")
