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
