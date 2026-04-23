class SimulationEngine:
    def __init__(self):
        self.clock = 0                      # The master global clock (in milliseconds)
        self.ready_queue = []               # Processes waiting for the CPU
        self.completed_processes = []       # Processes that have finished execution
        self.cpu_active_process = None      # The process currently holding the CPU
        
        # Hardware simulation constants
        self.CONTEXT_SWITCH_COST = 1        # Context switching takes 1 ms [cite: 13]
        self.INTERRUPT_COST = 0             # Interrupts consume 0 ms [cite: 13]

    def tick(self, milliseconds=1):
        """Advances the global simulation clock."""
        self.clock += milliseconds

    def add_to_ready_queue(self, process):
        """Moves a process into the ready state."""
        process.state = "READY"
        self.ready_queue.append(process)

    def context_switch(self, new_process):
        """Simulates swapping processes on the CPU."""
        if self.cpu_active_process is not None:
            self.cpu_active_process.state = "READY" # Or WAITING, depending on the event
            
        # Advance the clock by the cost of the context switch [cite: 13]
        self.tick(self.CONTEXT_SWITCH_COST) 
        
        self.cpu_active_process = new_process
        self.cpu_active_process.state = "RUNNING"
        
        # Record response time if this is the first time it gets the CPU
        if self.cpu_active_process.response_time == -1:
            self.cpu_active_process.response_time = self.clock - self.cpu_active_process.arrival_time

    def run_fcfs(self, incoming_processes):
        """Simulates the First-Come-First-Served scheduling algorithm."""
        print("\n--- Starting FCFS Simulation ---")
        
        # Keep running as long as there are processes yet to arrive, 
        # processes in the ready queue, or a process currently running
        while incoming_processes or self.ready_queue or self.cpu_active_process:
            
            # 1. Check for new arrivals at the current clock time
            arrived_this_tick = [p for p in incoming_processes if p.arrival_time == self.clock]
            for p in arrived_this_tick:
                self.add_to_ready_queue(p)
                incoming_processes.remove(p)
                print(f"[Time {self.clock} ms] {p.pid} arrived and joined Ready Queue.")

            # 2. Check if the currently running process has finished
            if self.cpu_active_process and self.cpu_active_process.remaining_time == 0:
                self.cpu_active_process.state = "TERMINATED"
                self.cpu_active_process.completion_time = self.clock
                
                # Calculate metrics for the finished process
                p = self.cpu_active_process
                p.turnaround_time = p.completion_time - p.arrival_time
                p.waiting_time = p.turnaround_time - p.burst_time
                
                self.completed_processes.append(p)
                print(f"[Time {self.clock} ms] {p.pid} TERMINATED.")
                self.cpu_active_process = None

            # 3. Assign CPU if it's idle and the ready queue has waiting processes
            if self.cpu_active_process is None and self.ready_queue:
                # FCFS: Take the first process that arrived (index 0)
                next_process = self.ready_queue.pop(0)
                
                print(f"[Time {self.clock} ms] Context Switch: CPU assigned to {next_process.pid}")
                self.context_switch(next_process) # This automatically ticks the clock by 1ms
                continue # Skip to the next loop iteration since 1ms passed during context switch

            # 4. Execute the active process
            if self.cpu_active_process:
                self.cpu_active_process.remaining_time -= 1
                
            # Advance the global clock by 1 millisecond
            self.tick(1)
            
        print("--- FCFS Simulation Complete ---")

    def run_round_robin(self, incoming_processes, time_quantum=3):
        """Simulates the Round Robin scheduling algorithm with a fixed time quantum."""
        print(f"\n--- Starting Round Robin Simulation (Quantum = {time_quantum}ms) ---")
        quantum_elapsed = 0
        
        while incoming_processes or self.ready_queue or self.cpu_active_process:
            
            # 1. Check for new arrivals at the current clock time
            arrived_this_tick = [p for p in incoming_processes if p.arrival_time == self.clock]
            for p in arrived_this_tick:
                self.add_to_ready_queue(p)
                incoming_processes.remove(p)
                print(f"[Time {self.clock} ms] {p.pid} arrived and joined Ready Queue.")

            # 2. Check if the currently running process needs to be removed
            if self.cpu_active_process:
                # Scenario A: The process finished completely
                if self.cpu_active_process.remaining_time == 0:
                    self.cpu_active_process.state = "TERMINATED"
                    self.cpu_active_process.completion_time = self.clock
                    
                    p = self.cpu_active_process
                    p.turnaround_time = p.completion_time - p.arrival_time
                    p.waiting_time = p.turnaround_time - p.burst_time
                    
                    self.completed_processes.append(p)
                    print(f"[Time {self.clock} ms] {p.pid} TERMINATED.")
                    self.cpu_active_process = None
                    quantum_elapsed = 0 # Reset the buzzer
                    
                # Scenario B: The 3ms quantum expired, but the process isn't done
                elif quantum_elapsed == time_quantum:
                    print(f"[Time {self.clock} ms] Quantum expired! {self.cpu_active_process.pid} preempted.")
                    self.add_to_ready_queue(self.cpu_active_process) # Back to the line!
                    self.cpu_active_process = None
                    quantum_elapsed = 0 # Reset the buzzer

            # 3. Assign CPU if it's idle and the ready queue has waiting processes
            if self.cpu_active_process is None and self.ready_queue:
                next_process = self.ready_queue.pop(0)
                
                print(f"[Time {self.clock} ms] Context Switch: CPU assigned to {next_process.pid}")
                self.context_switch(next_process) 
                quantum_elapsed = 0 # Ensure the new process gets a full 3ms
                continue # Skip to the next loop iteration (1ms passed during context switch)

            # 4. Execute the active process
            if self.cpu_active_process:
                self.cpu_active_process.remaining_time -= 1
                quantum_elapsed += 1 # Tick the buzzer closer to 3ms
                
            # Advance the global clock by 1 millisecond
            self.tick(1)
            
        print("--- Round Robin Simulation Complete ---")

    def run_sjf(self, incoming_processes):
        """Simulates the Shortest Job First (Non-Preemptive) scheduling algorithm."""
        print("\n--- Starting SJF Simulation ---")
        
        while incoming_processes or self.ready_queue or self.cpu_active_process:
            
            # 1. Check for new arrivals at the current clock time
            arrived_this_tick = [p for p in incoming_processes if p.arrival_time == self.clock]
            for p in arrived_this_tick:
                self.add_to_ready_queue(p)
                incoming_processes.remove(p)
                print(f"[Time {self.clock} ms] {p.pid} arrived and joined Ready Queue.")

            # 2. Check if the currently running process has finished
            if self.cpu_active_process and self.cpu_active_process.remaining_time == 0:
                self.cpu_active_process.state = "TERMINATED"
                self.cpu_active_process.completion_time = self.clock
                
                p = self.cpu_active_process
                p.turnaround_time = p.completion_time - p.arrival_time
                p.waiting_time = p.turnaround_time - p.burst_time
                
                self.completed_processes.append(p)
                print(f"[Time {self.clock} ms] {p.pid} TERMINATED.")
                self.cpu_active_process = None

            # 3. Assign CPU if it's idle
            if self.cpu_active_process is None and self.ready_queue:
                # SJF LOGIC: Sort the queue by burst_time and pick the smallest
                self.ready_queue.sort(key=lambda p: p.burst_time)
                next_process = self.ready_queue.pop(0)
                
                print(f"[Time {self.clock} ms] Context Switch: CPU assigned to {next_process.pid} (Burst: {next_process.burst_time}ms)")
                self.context_switch(next_process) # Applies the 1ms context switch cost 
                continue 

            # 4. Execute the active process
            if self.cpu_active_process:
                self.cpu_active_process.remaining_time -= 1
                
            # Advance the global clock
            self.tick(1)
            
        print("--- SJF Simulation Complete ---")

    def run_srtf(self, incoming_processes):
        """Simulates the Shortest Remaining Time First (Preemptive SJF) algorithm."""
        print("\n--- Starting SRTF (Preemptive SJF) Simulation ---")
        
        while incoming_processes or self.ready_queue or self.cpu_active_process:
            
            # 1. Check for new arrivals at the current clock time
            arrived_this_tick = [p for p in incoming_processes if p.arrival_time == self.clock]
            new_arrival_occured = False
            for p in arrived_this_tick:
                self.add_to_ready_queue(p)
                incoming_processes.remove(p)
                new_arrival_occured = True
                print(f"[Time {self.clock} ms] {p.pid} arrived (Burst: {p.burst_time}ms).")

            # 2. Check for Preemption: If a new shorter job arrived, swap!
            if new_arrival_occured and self.cpu_active_process:
                # Find the shortest job in the ready queue
                self.ready_queue.sort(key=lambda x: x.remaining_time)
                shortest_in_queue = self.ready_queue[0]
                
                if shortest_in_queue.remaining_time < self.cpu_active_process.remaining_time:
                    print(f"[Time {self.clock} ms] Preemption! {shortest_in_queue.pid} is shorter than {self.cpu_active_process.pid}.")
                    
                    # Return current process to queue and perform context switch
                    old_process = self.cpu_active_process
                    self.add_to_ready_queue(old_process)
                    self.cpu_active_process = None # Force a re-assignment in step 4

            # 3. Check if the currently running process has finished
            if self.cpu_active_process and self.cpu_active_process.remaining_time == 0:
                self.cpu_active_process.state = "TERMINATED"
                self.cpu_active_process.completion_time = self.clock
                
                p = self.cpu_active_process
                p.turnaround_time = p.completion_time - p.arrival_time # [cite: 19]
                p.waiting_time = p.turnaround_time - p.burst_time # [cite: 20]
                
                self.completed_processes.append(p)
                print(f"[Time {self.clock} ms] {p.pid} TERMINATED.")
                self.cpu_active_process = None

            # 4. Assign CPU if idle
            if self.cpu_active_process is None and self.ready_queue:
                self.ready_queue.sort(key=lambda p: p.remaining_time)
                next_process = self.ready_queue.pop(0)
                
                print(f"[Time {self.clock} ms] Context Switch: CPU assigned to {next_process.pid}")
                self.context_switch(next_process) # Applies 1ms cost 
                continue 

            # 5. Execute the active process
            if self.cpu_active_process:
                self.cpu_active_process.remaining_time -= 1
                
            self.tick(1)
            
        print("--- SRTF Simulation Complete ---")

    def run_priority_scheduling(self, incoming_processes):
        """Simulates Non-Preemptive Priority Scheduling."""
        print("\n--- Starting Priority Scheduling Simulation ---")
        
        while incoming_processes or self.ready_queue or self.cpu_active_process:
            
            # 1. Check for new arrivals at the current clock time 
            arrived_this_tick = [p for p in incoming_processes if p.arrival_time == self.clock]
            for p in arrived_this_tick:
                self.add_to_ready_queue(p)
                incoming_processes.remove(p)
                print(f"[Time {self.clock} ms] {p.pid} arrived (Priority: {p.priority}).")

            # 2. Check if the currently running process has finished
            if self.cpu_active_process and self.cpu_active_process.remaining_time == 0:
                self.cpu_active_process.state = "TERMINATED"
                self.cpu_active_process.completion_time = self.clock
                
                p = self.cpu_active_process
                p.turnaround_time = p.completion_time - p.arrival_time # [cite: 19]
                p.waiting_time = p.turnaround_time - p.burst_time # 
                
                self.completed_processes.append(p)
                print(f"[Time {self.clock} ms] {p.pid} TERMINATED.")
                self.cpu_active_process = None

            # 3. Assign CPU if it's idle [cite: 15]
            if self.cpu_active_process is None and self.ready_queue:
                # PRIORITY LOGIC: Sort by priority (assuming lower number = higher priority)
                self.ready_queue.sort(key=lambda p: p.priority)
                next_process = self.ready_queue.pop(0)
                
                print(f"[Time {self.clock} ms] Context Switch: CPU assigned to {next_process.pid}")
                self.context_switch(next_process) # Applies mandatory 1ms cost 
                continue 

            # 4. Execute the active process
            if self.cpu_active_process:
                self.cpu_active_process.remaining_time -= 1
                
            # Advance the global clock 
            self.tick(1)
            
        print("--- Priority Scheduling Simulation Complete ---")