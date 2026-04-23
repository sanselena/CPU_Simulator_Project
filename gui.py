import customtkinter as ctk
from tkinter import Canvas
import threading
import time
import sys
import copy # We need this for the Dry Run

# Import your actual backend
from engine import SimulationEngine
from CPU_Simulator_Project import generate_processes

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- Helper Classes ---
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

class DevNull:
    """A silent writer used to mute the engine during the dry run."""
    def write(self, msg): pass
    def flush(self): pass

class CPUSimulatorGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CPU Scheduling Simulator")
        self.geometry("1400x800")
        self.minsize(1200, 700)

        self.engine = None
        self.sim_thread = None
        self.is_running = False
        self.canvas_scale = 30 

        self.label_font = ("Roboto", 18, "bold")
        self.text_font = ("Roboto", 16)
        self.mono_font = ("Courier", 18) 

        # ==========================================
        # 1. COMMAND CENTER
        # ==========================================
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(pady=15, padx=10, fill="x")

        self.algo_label = ctk.CTkLabel(self.top_frame, text="Algorithm:", font=self.label_font)
        self.algo_label.pack(side="left", padx=(20, 10))
        
        self.algo_dropdown = ctk.CTkComboBox(
            self.top_frame, 
            values=["FCFS", "Round Robin (3ms)", "SJF", "Preemptive SRTF", "Priority"], 
            font=self.text_font,
            width=200
        )
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
        self.metrics_frame.pack(side="left", fill="y", padx=(0, 5))
        
        self.metrics_label = ctk.CTkLabel(self.metrics_frame, text="Averages", font=self.label_font)
        self.metrics_label.pack(pady=10)
        
        self.metrics_textbox = ctk.CTkTextbox(self.metrics_frame, font=self.text_font, state="disabled")
        self.metrics_textbox.pack(pady=5, padx=10, fill="both", expand=True)

        self.queue_frame = ctk.CTkFrame(self.middle_frame)
        self.queue_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        self.queue_label = ctk.CTkLabel(self.queue_frame, text="Live System Logs & Queue", font=self.label_font)
        self.queue_label.pack(pady=10)
        
        self.queue_textbox = ctk.CTkTextbox(self.queue_frame, font=self.text_font, state="disabled")
        self.queue_textbox.pack(pady=5, padx=10, fill="both", expand=True)

        self.table_frame = ctk.CTkFrame(self.middle_frame) 
        self.table_frame.pack(side="right", fill="y", padx=(5, 0))

        self.table_label = ctk.CTkLabel(self.table_frame, text="Process Results Table", font=self.label_font)
        self.table_label.pack(pady=10)

        self.table_textbox = ctk.CTkTextbox(
            self.table_frame, 
            font=self.mono_font, 
            state="disabled", 
            wrap="none", 
            width=600 
        )
        self.table_textbox.pack(pady=5, padx=10, fill="both", expand=True)

        # ==========================================
        # 3. TIMELINE
        # ==========================================
        self.bottom_frame = ctk.CTkFrame(self, height=200)
        self.bottom_frame.pack(pady=15, padx=10, fill="x")
        
        self.timeline_label = ctk.CTkLabel(self.bottom_frame, text="CPU Execution Timeline", font=self.label_font)
        self.timeline_label.pack(pady=5)
        
        self.timeline_canvas = Canvas(self.bottom_frame, height=120, bg="#1a1a1a", highlightthickness=0)
        self.timeline_canvas.pack(fill="x", padx=20, pady=(0, 15))

    def start_simulation_thread(self):
        if self.is_running: return

        self.queue_textbox.configure(state="normal")
        self.queue_textbox.delete("1.0", "end")
        self.queue_textbox.configure(state="disabled")
        
        self.metrics_textbox.configure(state="normal")
        self.metrics_textbox.delete("1.0", "end")
        self.metrics_textbox.configure(state="disabled")

        self.table_textbox.configure(state="normal")
        self.table_textbox.delete("1.0", "end")
        self.table_textbox.configure(state="disabled")

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
        self.update_idletasks()
        canvas_width = self.timeline_canvas.winfo_width() - 60 

        print("--- Initializing Process Load ---")
        my_processes = generate_processes(num_processes=5, max_arrival_time=10, max_burst_time=8)
        selected_algo = self.algo_dropdown.get()

        # =================================================================
        # THE PERFECT SCALING FIX: THE DRY RUN
        # We silently run the simulation instantly in the background 
        # to find the EXACT completion time, then set the canvas scale.
        # =================================================================
        dry_processes = copy.deepcopy(my_processes)
        dummy_engine = SimulationEngine()
        
        original_stdout = sys.stdout
        sys.stdout = DevNull() # Mute output so it doesn't print to the UI twice
        
        try:
            if selected_algo == "FCFS":
                dummy_engine.run_fcfs(dry_processes)
            elif selected_algo == "Round Robin (3ms)":
                dummy_engine.run_round_robin(dry_processes, time_quantum=3)
            elif selected_algo == "SJF":
                dummy_engine.run_sjf(dry_processes)
            elif selected_algo == "Preemptive SRTF":
                dummy_engine.run_srtf(dry_processes)
            elif selected_algo == "Priority":
                dummy_engine.run_priority_scheduling(dry_processes)
        except Exception:
            pass # Catching in case user hits stop during dry run
            
        sys.stdout = original_stdout # Turn UI printing back on
        
        # We now know exactly how long the simulation will take! (+1 for a tiny right margin)
        exact_total_time = dummy_engine.clock
        self.canvas_scale = canvas_width / max(1, (exact_total_time + 1))
        # =================================================================

        for p in my_processes:
            priority_str = f" | Prio: {getattr(p, 'priority', 'N/A')}" if hasattr(p, 'priority') else ""
            print(f"ID: {p.pid} | Arrive: {p.arrival_time}ms | Burst: {p.burst_time}ms{priority_str}")

        original_tick = self.engine.tick
        def controlled_tick(milliseconds=1):
            if not self.is_running: sys.exit()
            curr_c = self.engine.clock
            act_p = self.engine.cpu_active_process
            pid = act_p.pid if act_p else "CS"
            
            self.after(0, self.draw_timeline_slice, curr_c, pid)
            time.sleep(0.4) 
            original_tick(milliseconds)
            
        self.engine.tick = controlled_tick
        
        try:
            if selected_algo == "FCFS":
                self.engine.run_fcfs(my_processes)
            elif selected_algo == "Round Robin (3ms)":
                self.engine.run_round_robin(my_processes, time_quantum=3)
            elif selected_algo == "SJF":
                self.engine.run_sjf(my_processes)
            elif selected_algo == "Preemptive SRTF":
                self.engine.run_srtf(my_processes)
            elif selected_algo == "Priority":
                self.engine.run_priority_scheduling(my_processes)
        except SystemExit: pass
            
        sys.stdout = sys.__stdout__
        self.is_running = False
        if self.engine.completed_processes:
            self.display_final_metrics()

    def draw_timeline_slice(self, clock, pid):
        x1 = clock * self.canvas_scale
        x2 = x1 + self.canvas_scale
        y1, y2 = 25, 85

        if pid == "CS":
            color = "#333333"
        else:
            if pid not in self.process_colors:
                self.process_colors[pid] = self.color_palette[len(self.process_colors) % len(self.color_palette)]
            color = self.process_colors[pid]

        self.timeline_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#1a1a1a", width=1)

        if pid != self.last_drawn_pid and pid != "CS":
            self.timeline_canvas.create_text(x1 + 5, 55, text=pid, fill="black", font=("Roboto", 14, "bold"), anchor="w")
        
        self.timeline_canvas.create_text(x1, 105, text=str(clock), fill="#777777", font=("Roboto", 10), anchor="n")

        self.last_drawn_pid = pid
        self.timeline_canvas.config(scrollregion=self.timeline_canvas.bbox("all"))

    def display_final_metrics(self):
        completed = self.engine.completed_processes
        if not completed: return

        n = len(completed)
        avg_tat = sum(p.turnaround_time for p in completed) / n
        avg_wt = sum(p.waiting_time for p in completed) / n
        avg_rt = sum(p.response_time for p in completed) / n
        
        total_time = self.engine.clock
        busy_time = sum(p.burst_time for p in completed)
        utilization = (busy_time / total_time) * 100 if total_time > 0 else 0
        throughput = n / total_time if total_time > 0 else 0

        self.metrics_textbox.configure(state="normal")
        self.metrics_textbox.insert("end", f"Processor Utilization:\n{utilization:.2f}%\n\n")
        self.metrics_textbox.insert("end", f"Throughput:\n{throughput:.4f} p/ms\n\n")
        self.metrics_textbox.insert("end", f"Avg Turnaround Time:\n{avg_tat:.2f} ms\n\n")
        self.metrics_textbox.insert("end", f"Avg Waiting Time:\n{avg_wt:.2f} ms\n\n")
        self.metrics_textbox.insert("end", f"Avg Request Time:\n{avg_rt:.2f} ms\n")
        self.metrics_textbox.configure(state="disabled")

        self.table_textbox.configure(state="normal")
        header = f"{'PID':<4} | {'Arrive':<6} | {'Burst':<5} | {'TAT':<4} | {'Wait':<4} | {'Req':<4}\n"
        self.table_textbox.insert("end", header)
        self.table_textbox.insert("end", "-" * 50 + "\n")
        
        for p in sorted(completed, key=lambda x: x.pid):
            row = f"{p.pid:<4} | {p.arrival_time:<4}ms | {p.burst_time:<3}ms | {p.turnaround_time:<2}ms | {p.waiting_time:<2}ms | {p.response_time:<2}ms\n"
            self.table_textbox.insert("end", row)
        
        self.table_textbox.configure(state="disabled")

if __name__ == "__main__":
    app = CPUSimulatorGUI()
    app.mainloop()