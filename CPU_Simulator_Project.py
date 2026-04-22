import random
from process import Process
from engine import SimulationEngine

def generate_processes(num_processes, max_arrival_time=20, max_burst_time=15):
    """Generates a list of random processes."""
    processes = []
    for i in range(1, num_processes + 1):
        # Time unit is in milliseconds as requested
        arrival_time = random.randint(0, max_arrival_time)
        burst_time = random.randint(1, max_burst_time)
        processes.append(Process(pid=f"P{i}", arrival_time=arrival_time, burst_time=burst_time))
    
    # Sort by arrival time so they enter the system chronologically
    processes.sort(key=lambda p: p.arrival_time)
    return processes

if __name__ == "__main__":
    # 1. Initialize the Simulation Engine
    engine = SimulationEngine()
    
    # 2. Generate a small batch of 5 random processes
    print("--- Generating Processes ---")
    my_processes = generate_processes(num_processes=5, max_arrival_time=10, max_burst_time=8)
    
    for p in my_processes:
        print(f"Created: {p.pid} | Arrival: {p.arrival_time}ms | Burst: {p.burst_time}ms")
    
    # 3. Run the FCFS Algorithm
    #engine.run_fcfs(my_processes)
    engine.run_round_robin(my_processes, time_quantum=3)  
    
    # 4. Print final metrics to ensure the math checks out
    print("\n--- Final Process Metrics ---")
    for p in engine.completed_processes:
        print(f"{p.pid}: Turnaround Time = {p.turnaround_time}ms, Waiting Time = {p.waiting_time}ms")
