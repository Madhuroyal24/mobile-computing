"""B1: Instrumented background upload scheduler; FIFO vs priority."""
from dataclasses import dataclass
from typing import List

@dataclass
class Job:
    job_id: str
    priority: int
    critical: bool = False

def run_scheduler(jobs: List[Job], strategy: str, scenario: str):
    # State values are deliberately simulated and printed at every decision.
    states = {
        "good": {"battery": 82, "network": "Wi-Fi", "doze": False, "permission": True},
        "low_battery": {"battery": 8, "network": "Wi-Fi", "doze": True, "permission": True},
        "permission_revoked": {"battery": 70, "network": "Wi-Fi", "doze": False, "permission": True},
    }
    state = states[scenario].copy()
    queue = jobs.copy()
    if strategy == "FIFO":
        ordered = queue
    else:
        ordered = sorted(queue, key=lambda j: (not j.critical, -j.priority, j.job_id))
    enqueued = len(ordered); deferred = cancelled = success = 0
    active = max_workers = 0
    print(f"\n[{scenario.upper()} | {strategy}]")
    print(f"ENQUEUED={enqueued}")
    for index, job in enumerate(ordered, 1):
        active = 1
        max_workers = max(max_workers, active)
        print(f"DECISION {index}: job={job.job_id}, battery={state['battery']}%, "
              f"network={state['network']}, doze={state['doze']}, permission={state['permission']}")
        if scenario == "permission_revoked" and index == 2:
            state["permission"] = False
            print("EVENT: permission revoked while processing")
        if not state["permission"]:
            cancelled += 1
            print(f"{job.job_id}: CANCELLED (permission unavailable)")
        elif state["battery"] < 15 or state["doze"]:
            deferred += 1
            print(f"{job.job_id}: DEFERRED (battery/Doze constraint)")
        elif state["network"] not in ("Wi-Fi", "Mobile"):
            deferred += 1
            print(f"{job.job_id}: DEFERRED (no network)")
        else:
            success += 1
            print(f"{job.job_id}: UPLOADED")
        active = 0
    print(f"SUMMARY: enqueued={enqueued}, deferred={deferred}, cancelled={cancelled}, "
          f"successful={success}, max_workers={max_workers}, backlog={enqueued-success-cancelled}")
    return enqueued, deferred, cancelled, success, max_workers

if __name__ == "__main__":
    jobs = [Job("J1", 1), Job("J2", 5, True), Job("J3", 2), Job("J4", 4, True), Job("J5", 3)]
    print("B1 – BACKGROUND WORK SCHEDULER")
    print("Priority rule: critical jobs first, then higher priority, then job ID.")
    for scenario in ("good", "low_battery", "permission_revoked"):
        for strategy in ("FIFO", "PRIORITY"):
            run_scheduler(jobs, strategy, scenario)
