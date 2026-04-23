import customtkinter as ctk
from tkinter import Canvas
import threading
import time
import sys

# Import your actual backend!
from engine import SimulationEngine
from CPU_Simulator_Project import generate_processes

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PrintRedirector:
    def __init__(self, textbox):
        self.textbox = textbox

    def write(self, message):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", message)
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def flush(self):
        pass

class CPUSimulatorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CPU Scheduling Simulator")
        self.geometry("1100x800")
        self.minsize(900, 700)

        # State Variables
        self.engine = None
        self.sim_thread = None
        self.is_running = False
        self.canvas_scale = 30 # Pixels per ms

        # Global Font Styles
        self.label_font = ("Roboto", 18, "bold")
        self.text_font = ("Roboto", 16)

        # ==========================================
        # 1. COMMAND CENTER
        # ==========================================
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(pady=15, padx=10, fill="x")

        self.algo_label = ctk.CTkLabel(self.top_frame, text="Algorithm:", font=self.label_font)
        self.algo_label.pack(side="left", padx=(20, 10))
        
        self.algo_dropdown = ctk.CTkComboBox(self.top_frame, values=["FCFS", "Round Robin (3ms)", "SJF"], font=self.text_font)
        self.algo_dropdown.pack(side="left", padx=10)

        self.run_button = ctk.CTkButton(
            self.top_frame, 
            text="Generate & Run", 
            command=self.start_simulation_thread,
            fg_color="#6A5ACD",
            hover_color="#483D8B",
            font=self.label_font,
            height=40
        )
        self.run_button.pack(side="left", expand=True)

        self.stop_button = ctk.CTkButton(
            self.top_frame, 
            text="Stop (Space)", 
            fg_color="#8B0000", 
            hover_color="#FF0000", 
            command=self.stop_simulation,
            font=self.label_font,
            height=40
        )
        self.stop_button.pack(side="right", padx=20)
        
        self.bind("<space>", self.stop_simulation)

        # ==========================================
        # 2. LIVE ARENA
        # ==========================================
        self.middle_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.middle_frame.pack(pady=5, padx=10, fill="both", expand=True)

        self.metrics_frame = ctk.CTkFrame(self.middle_frame, width=250)
        self.metrics_frame.pack(side="left", fill="y", padx=(0, 10))
        
        self.metrics_label = ctk.CTkLabel(self.metrics_frame, text="Metrics", font=self.label_font)
        self.metrics_label.pack(pady=10)
        
        self.metrics_textbox = ctk.CTkTextbox(self.metrics_frame, font=self.text_font, state="disabled")
        self.metrics_textbox.pack(pady=5, padx=10, fill="both", expand=True)

        self.queue_frame = ctk.CTkFrame(self.middle_frame)
        self.queue_frame.pack(side="right", fill="both", expand=True)
        
        self.queue_label = ctk.CTkLabel(self.queue_frame, text="Live System Logs & Queue", font=self.label_font)
        self.queue_label.pack(pady=10)
        
        self.queue_textbox = ctk.CTkTextbox(self.queue_frame, font=self.text_font, state="disabled")
        self.queue_textbox.pack(pady=5, padx=10, fill="both", expand=True)

        # ==========================================
        # 3. TIMELINE (Canvas)
        # ==========================================
        self.bottom_frame = ctk.CTkFrame(self, height=200)
        self.bottom_frame.pack(pady=15, padx=10, fill="x")
        
        self.timeline_label = ctk.CTkLabel(self.bottom_frame, text="CPU Execution Timeline", font=self.label_font)
        self.timeline_label.pack(pady=5)
        
        self.timeline_canvas = Canvas(self.bottom_frame, height=120, bg="#1a1a1a", highlightthickness=0)
        self.timeline_canvas.pack(fill="x", padx=20, pady=(0, 15))

    def start_simulation_thread(self):
        if self.is_running: return

        # Reset UI elements
        self.queue_textbox.configure(state="normal")
        self.queue_textbox.delete("1.0", "end")
        self.queue_textbox.configure(state="disabled")
        self.metrics_textbox.configure(state="normal")
        self.metrics_textbox.delete("1.0", "end")
        self.metrics_textbox.configure(state="disabled")
        self.timeline_canvas.delete("all")
        
        self.process_colors = {}
        self.color_palette = ["#FF5252", "#448AFF", "#69F0AE", "#FFD740", "#E040FB", "#00BCD4"]
        self.last_drawn_pid = None

        sys.stdout = PrintRedirector(self.queue_textbox)
        self.is_running = True
        self.sim_thread = threading.Thread(target=self._run_engine_logic)
        self.sim_thread.start()

    def stop_simulation(self, event=None):
        if self.is_running:
            self.is_running = False
            print("\n[!] INTERRUPTED BY USER.")

    def _run_engine_logic(self):
        self.engine = SimulationEngine()
        
        print("--- Initializing Process Load ---")
        my_processes = generate_processes(num_processes=5, max_arrival_time=10, max_burst_time=8)
        
        # FIXED SCALING: Use a reliable width measurement or fixed default
        # We calculate scale based on available space vs expected time
        total_burst = sum(p.burst_time for p in my_processes)
        expected_time = total_burst + 15 # Add buffer for context switches
        
        # Calculate scale to fit at least 1000px width
        self.canvas_scale = max(30, 1000 / expected_time) 

        for p in my_processes:
            print(f"ID: {p.pid} | Arrive: {p.arrival_time}ms | Burst: {p.burst_time}ms")

        original_tick = self.engine.tick
        def controlled_tick(milliseconds=1):
            if not self.is_running: sys.exit()
            curr_c = self.engine.clock
            act_p = self.engine.cpu_active_process
            pid = act_p.pid if act_p else "CS"
            
            # Send to main thread for drawing
            self.after(0, self.draw_timeline_slice, curr_c, pid)
            
            time.sleep(0.4) 
            original_tick(milliseconds)
            
        self.engine.tick = controlled_tick
        selected_algo = self.algo_dropdown.get()
        
        try:
            if selected_algo == "FCFS":
                self.engine.run_fcfs(my_processes)
            elif selected_algo == "Round Robin (3ms)":
                self.engine.run_round_robin(my_processes, time_quantum=3)
            elif selected_algo == "SJF":
                print("\n[System] Ready for SJF Merge...")
        except SystemExit: pass
            
        sys.stdout = sys.__stdout__
        self.is_running = False
        if self.engine.completed_processes:
            self.display_final_metrics()

    def draw_timeline_slice(self, clock, pid):
        """Draws exactly 1ms with markers for every millisecond."""
        x1 = clock * self.canvas_scale
        x2 = x1 + self.canvas_scale
        y1, y2 = 25, 85

        if pid == "CS":
            color = "#333333"
        else:
            if pid not in self.process_colors:
                self.process_colors[pid] = self.color_palette[len(self.process_colors) % len(self.color_palette)]
            color = self.process_colors[pid]

        # Draw the 1ms slice
        self.timeline_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#1a1a1a", width=1)

        # Label the process if it's the first time we see it in this block
        if pid != self.last_drawn_pid and pid != "CS":
            self.timeline_canvas.create_text(x1 + 5, 55, text=pid, fill="black", font=("Roboto", 14, "bold"), anchor="w")
        
        # Reverted: Now draws every single ms marker
        self.timeline_canvas.create_text(x1 + (self.canvas_scale/2), 100, text=str(clock), fill="#777777", font=("Roboto", 10))

        self.last_drawn_pid = pid
        # Auto-update scroll to keep the newest block in view
        self.timeline_canvas.config(scrollregion=self.timeline_canvas.bbox("all"))

    def display_final_metrics(self):
        self.metrics_textbox.configure(state="normal")
        self.metrics_textbox.insert("end", "--- RESULTS ---\n\n")
        # Ensure we show all required metrics: Turnaround, Waiting, etc.
        for p in self.engine.completed_processes:
            self.metrics_textbox.insert("end", f"[{p.pid}]\nWait: {p.waiting_time}ms\nTurn: {p.turnaround_time}ms\n\n")
        self.metrics_textbox.configure(state="disabled")

if __name__ == "__main__":
    app = CPUSimulatorGUI()
    app.mainloop()