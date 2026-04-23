import random
import copy
from process import Process
from engine import SimulationEngine

def generate_processes(num_processes, max_arrival_time=20, max_burst_time=15):
    """Generates a list of random processes with priorities[cite: 12]."""
    processes = []
    for i in range(1, num_processes + 1):
        # Time unit is in milliseconds as requested [cite: 12]
        arrival_time = random.randint(0, max_arrival_time)
        burst_time = random.randint(1, max_burst_time)
        priority = random.randint(1, 5) 
        
        processes.append(Process(
            pid=f"P{i}", 
            arrival_time=arrival_time, 
            burst_time=burst_time, 
            priority=priority
        ))
    
    # Sort by arrival time so they enter the system chronologically
    processes.sort(key=lambda p: p.arrival_time)
    return processes

def display_metrics(engine):
    """Calculates and prints performance metrics [cite: 16-21]."""
    completed = engine.completed_processes
    if not completed:
        return

    # Individual Results for the Report 
    print("\n--- Individual Process Results ---")
    print(f"{'PID':<6} | {'Arrival':<8} | {'Burst':<8} | {'TAT':<8} | {'Waiting':<8} | {'Request':<8}")
    print("-" * 60)
    for p in sorted(completed, key=lambda x: x.pid):
        print(f"{p.pid:<6} | {p.arrival_time:<6}ms | {p.burst_time:<6}ms | {p.turnaround_time:<6}ms | {p.waiting_time:<6}ms | {p.response_time:<6}ms")

    # Averages
    n = len(completed)
    avg_tat = sum(p.turnaround_time for p in completed) / n
    avg_wt = sum(p.waiting_time for p in completed) / n
    avg_rt = sum(p.response_time for p in completed) / n
    
    total_time = engine.clock
    busy_time = sum(p.burst_time for p in completed)
    utilization = (busy_time / total_time) * 100 if total_time > 0 else 0
    throughput = n / total_time if total_time > 0 else 0

    print("\n--- Performance Metrics Evaluation ---")
    print(f"Processor Utilization: {utilization:.2f}% [cite: 17]")
    print(f"Throughput: {throughput:.4f} processes/ms [cite: 18]")
    print(f"Average Turnaround Time: {avg_tat:.2f} ms [cite: 19]")
    print(f"Average Waiting Time: {avg_wt:.2f} ms [cite: 20]")
    print(f"Average Request Time: {avg_rt:.2f} ms [cite: 21]")

if __name__ == "__main__":
    print("=== BIL342 CPU Scheduling Simulator ===")
    num_p = 5
    base_processes = generate_processes(num_processes=num_p)
    
    print("\nSelect Algorithm[cite: 24]:")
    print("1. FCFS\n2. Round Robin (3ms)\n3. SJF\n4. SRTF (Preemptive)\n5. Priority")
    choice = input("Enter choice (1-5): ")

    # Prepare simulation data
    test_processes = copy.deepcopy(base_processes)
    engine = SimulationEngine()

    # --- VERIFICATION TABLE: Prints before the flow ---
    print("\n--- Process Input Data (Use this to verify the flow) ---")
    print(f"{'PID':<6} | {'Arrival':<10} | {'Burst':<10} | {'Priority':<10}")
    print("-" * 45)
    for p in test_processes:
        print(f"{p.pid:<6} | {p.arrival_time:<8}ms | {p.burst_time:<8}ms | {p.priority:<10}")
    print("-" * 45)

    # 3. Execution
    if choice == '1':
        engine.run_fcfs(test_processes)
    elif choice == '2':
        engine.run_round_robin(test_processes, time_quantum=3) 
    elif choice == '3':
        engine.run_sjf(test_processes)
    elif choice == '4':
        engine.run_srtf(test_processes)
    elif choice == '5':
        engine.run_priority_scheduling(test_processes)
    else:
        print("Invalid selection.")

    # 4. Final Metrics
    display_metrics(engine)