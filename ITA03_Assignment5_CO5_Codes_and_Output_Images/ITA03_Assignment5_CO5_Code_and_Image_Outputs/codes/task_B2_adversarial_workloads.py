"""B2: Same-size easy and difficult workloads through the B1 constraints."""
def execute(name, events):
    battery, doze, permission, network = 60, False, True, "Wi-Fi"
    processed = deferred = cancelled = delivered = retries = 0
    print(f"\n{name}: {len(events)} records (same size)")
    for i, event in enumerate(events, 1):
        processed += 1
        # Each event describes the constraint state at its attempt.
        battery, doze, permission, network = event
        print(f"item {i:02d}: battery={battery:02d}%, doze={doze}, "
              f"permission={permission}, network={network}")
        if not permission:
            cancelled += 1
            print("  -> CANCELLED")
        elif battery < 15 or doze or network == "OFFLINE":
            deferred += 1
            retries += 1
            print("  -> DEFERRED; retry when constraints improve")
        else:
            delivered += 1
            print("  -> DELIVERED")
    print(f"RESULT: processed={processed}, deferrals={deferred}, retries={retries}, "
          f"cancelled={cancelled}, delivered={delivered}")
    return processed, deferred, retries, cancelled, delivered

if __name__ == "__main__":
    easy = [(75,False,True,"Wi-Fi"), (72,False,True,"Wi-Fi"),
            (68,False,True,"Mobile"), (65,False,True,"Wi-Fi"),
            (60,False,True,"Wi-Fi"), (58,False,True,"Wi-Fi"),
            (55,False,True,"Mobile"), (52,False,True,"Wi-Fi"),
            (50,False,True,"Wi-Fi"), (48,False,True,"Wi-Fi")]
    hard = [(9,True,True,"Wi-Fi"), (8,True,True,"OFFLINE"),
            (12,False,True,"OFFLINE"), (10,True,True,"Wi-Fi"),
            (7,True,True,"OFFLINE"), (13,False,True,"OFFLINE"),
            (11,True,True,"Wi-Fi"), (6,True,True,"OFFLINE"),
            (14,False,True,"OFFLINE"), (5,True,True,"Wi-Fi")]
    print("B2 – ADVERSARIAL WORKLOAD COMPARISON")
    print("Prediction: the difficult workload will defer more often because it repeatedly violates battery, Doze or network constraints.")
    a = execute("WORKLOAD A – EASY", easy)
    b = execute("WORKLOAD B – ADVERSARIAL", hard)
    print("\nCOMPARISON")
    print(f"same_input_size={a[0]} records; easy_delivered={a[4]}; hard_delivered={b[4]}")
    print(f"easy_deferrals={a[1]}; hard_deferrals={b[1]}")
