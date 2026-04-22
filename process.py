class Process:
    def __init__(self, pid, arrival_time, burst_time):
        self.pid = pid                      # Unique ID for the process
        self.arrival_time = arrival_time    # When the process enters the system
        self.burst_time = burst_time        # Total CPU time needed
        
        # Dynamic execution variables
        self.remaining_time = burst_time    # Time left to finish execution
        self.state = "NEW"                  # States: NEW, READY, RUNNING, WAITING, TERMINATED
        
        # Metrics tracking
        self.completion_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = -1             # -1 indicates the CPU has never picked it up yet

    def __repr__(self):
        return f"Process({self.pid}, Arrival:{self.arrival_time}, Burst:{self.burst_time}, State:{self.state})"
