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

    # ==========================================
    # CANVAS DRAWING LOGIC
    # ==========================================
    def draw_timeline_slice(self, clock, pid):
        """Draws a 1-millisecond chunk of the Gantt chart."""
        scale = 25  # 25 Pixels per millisecond
        x1 = clock * scale
        x2 = x1 + scale
        y1 = 20
        y2 = 80

        # Assign colors dynamically
        if pid == "CS":
            color = "#424242" # Dark Gray for Context Switch overhead
        else:
            if pid not in self.process_colors:
                self.process_colors[pid] = self.color_palette[len(self.process_colors) % len(self.color_palette)]
            color = self.process_colors[pid]

        # Draw the 1ms block (setting outline to the same color makes it look like one solid bar)
        self.timeline_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)

        # If the process just changed, stamp the process ID text on the block
        if pid != self.last_drawn_pid and pid != "CS":
            self.timeline_canvas.create_text(x1 + 5, 50, text=pid, fill="black", font=("Roboto", 12, "bold"), anchor="w")
        
        # Draw a tiny millisecond marker at the bottom
        self.timeline_canvas.create_text(x1, 95, text=str(clock), fill="#9E9E9E", font=("Roboto", 8), anchor="w")

        self.last_drawn_pid = pid
        
        # Ensures the canvas becomes horizontally scrollable if the simulation runs long
        self.timeline_canvas.config(scrollregion=self.timeline_canvas.bbox("all"))

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
