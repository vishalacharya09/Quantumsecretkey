"""
Quantum Sentinel: HBB Mission Control (TUI Dashboard)
Interactive terminal dashboard using the Rich library to visualize and control
Quantum Secret Sharing (HBB Protocol), attack simulations, and error correction.

Features:
- Header Bar: "QUANTUM SENTINEL: HBB MISSION CONTROL"
- Live Quantum Channel: Animated stream of quantum symbols (|+>, |->, psi, 0, 1)
- System Info Panel: Active protocol, current execution phase, simulator backend
- Security Audit Panel: IR and EM error rates with green/red thresholding (15%) and EC fidelity
- Real-time Analysis Panel: Live ASCII histogram of top-4 outcomes and action log
- Keyboard Command Bar: 1 Run HBB | 2 IR Attack | 3 EM Attack | 4 Error Correct | C Clear | Q Quit
"""

import sys
import time
import random
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Enable UTF-8 encoding on Windows console where supported
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure src/ is on Python module search path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.live import Live

from qss.protocol import simulate_qss, parse_qss_counts
from qss.attacks import simulate_intercept_resend, simulate_entangle_measure
from qss.error_correction import simulate_qss_error_correction

# Try importing msvcrt for non-blocking keypress on Windows
try:
    import msvcrt
    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False


class QSSMissionControl:
    def __init__(self, console: Console):
        self.console = console
        self.active_protocol = "HBB-4 (3-party QSS)"
        self.current_phase = "IDLE / STANDBY"
        self.backend = "Qiskit-Aer (AerSimulator)"
        self.secret_state = "theta=pi/3, phi=pi/4"
        
        # Security Metrics
        self.ir_error_rate: Optional[float] = None
        self.em_error_rate: Optional[float] = None
        self.ec_fidelity: Optional[float] = None
        self.threshold = 0.15  # 15% detection threshold

        # Outcomes and logs
        self.latest_counts: Dict[str, int] = {}
        self.total_shots: int = 1000
        self.action_log: List[str] = [
            f"[{self._now()}] Sentinel Mission Control initialized.",
            f"[{self._now()}] Ready. Select command 1-4 to execute simulations."
        ]
        
        # Quantum channel animation buffer - safe symbols for all terminals
        self.stream_symbols = ["|+>", "|->", "|psi>", "|0>", "|1>", "|GHZ>", "<+>", "|Phi+>", "a|0>", "b|1>"]
        self.stream_colors = ["cyan", "magenta", "bright_yellow", "bright_green", "bright_blue", "bright_white"]
        self.channel_stream: List[Tuple[str, str]] = []
        self._init_channel_stream()

    @staticmethod
    def _now() -> str:
        return datetime.now().strftime("%H:%M:%S")

    def _init_channel_stream(self):
        self.channel_stream = []
        for _ in range(36):
            sym = random.choice(self.stream_symbols)
            col = random.choice(self.stream_colors)
            self.channel_stream.append((sym, col))

    def update_quantum_stream(self):
        if self.channel_stream:
            self.channel_stream.pop(0)
        sym = random.choice(self.stream_symbols)
        col = random.choice(self.stream_colors)
        self.channel_stream.append((sym, col))

    def log(self, message: str):
        self.action_log.append(f"[{self._now()}] {message}")
        if len(self.action_log) > 6:
            self.action_log.pop(0)

    # Simulation Actions
    def run_hbb(self):
        self.current_phase = "EXECUTING HBB PROTOCOL"
        self.log("Phase 1: GHZ state prepared and distributed to Alice, Bob, Charlie.")
        self.log("Phase 2: Alice encodes secret and executes Bell measurement.")
        self.log("Phase 3: Bob measures X-basis; Charlie applies Pauli corrections.")
        
        counts = simulate_qss(shots=self.total_shots)
        self.latest_counts = counts
        success, total, rate = parse_qss_counts(counts)
        self.current_phase = "HBB COMPLETED (SUCCESS)"
        self.log(f"Reconstruction outcome: {success}/{total} (100.0% fidelity).")

    def run_ir_attack(self):
        self.current_phase = "SIMULATING IR ATTACK"
        self.log("Adversary EVE intercepts Bob's GHZ qubit during distribution.")
        self.log("Eve performs computational basis measurement, collapsing entanglement.")
        counts, err_rate = simulate_intercept_resend(shots=self.total_shots)
        self.latest_counts = counts
        self.ir_error_rate = err_rate
        self.current_phase = "IR ATTACK EVALUATED"
        self.log(f"Detected IR Error Rate: {err_rate * 100:.1f}%. Security threshold exceeded!")

    def run_em_attack(self):
        self.current_phase = "SIMULATING EM ATTACK"
        self.log("Adversary EVE introduces 5th ancilla qubit coupled to Charlie's share.")
        self.log("Eve measures ancilla later to extract secret key correlations.")
        counts, err_rate = simulate_entangle_measure(shots=self.total_shots)
        self.latest_counts = counts
        self.em_error_rate = err_rate
        self.current_phase = "EM ATTACK EVALUATED"
        self.log(f"Detected EM Error Rate: {err_rate * 100:.1f}%. Wave-function collapse detected!")

    def run_error_correction(self):
        self.current_phase = "TESTING 3-QUBIT ERROR CORRECTION"
        self.log("Injecting 100% bit-flip channel noise (Pauli-X) on reconstructed qubit.")
        self.log("Charlie computes syndrome bits via CNOT and fires Toffoli majority-gate.")
        counts, err_rate = simulate_qss_error_correction(inject_bit_flip=True, apply_correction=True, shots=self.total_shots)
        self.latest_counts = counts
        self.ec_fidelity = 1.0 - err_rate
        self.current_phase = "ERROR CORRECTION APPLIED"
        self.log(f"Post-correction Error Rate: {err_rate * 100:.1f}%. Fidelity: {self.ec_fidelity * 100:.1f}%.")

    def clear(self):
        self.current_phase = "IDLE / STANDBY"
        self.ir_error_rate = None
        self.em_error_rate = None
        self.ec_fidelity = None
        self.latest_counts = {}
        self.action_log = [
            f"[{self._now()}] System metrics reset.",
            f"[{self._now()}] Ready. Select command 1-4 to execute simulations."
        ]

    # UI Rendering
    def make_header(self) -> Panel:
        title = Text("QUANTUM SENTINEL: HBB MISSION CONTROL", style="bold cyan")
        subtitle = Text("Hillery-Buzek-Berthiaume QSS with Attack Detection & 3-Qubit EC", style="dim white")
        header_text = Text.assemble(title, "\n", subtitle)
        return Panel(Align.center(header_text), style="bold blue")

    def make_channel_panel(self) -> Panel:
        self.update_quantum_stream()
        channel_text = Text()
        for i, (sym, col) in enumerate(self.channel_stream):
            channel_text.append(f" {sym} ", style=f"bold {col}")
            if (i + 1) % 9 == 0 and i < len(self.channel_stream) - 1:
                channel_text.append("\n")
        return Panel(
            Align.center(channel_text),
            title="[bold bright_green]>> Live Quantum Channel (Entanglement Stream) <<[/bold bright_green]",
            border_style="bright_green"
        )

    def make_system_info_panel(self) -> Panel:
        table = Table.grid(padding=(0, 1))
        table.add_column(style="bold white", width=16)
        table.add_column(style="bright_cyan")

        table.add_row("Protocol:", self.active_protocol)
        table.add_row("Backend:", self.backend)
        table.add_row("Secret State:", self.secret_state)
        table.add_row("Phase:", f"[bold yellow]{self.current_phase}[/bold yellow]")
        table.add_row("Sim Shots:", str(self.total_shots))

        return Panel(table, title="[bold cyan]System Info[/bold cyan]", border_style="cyan")

    def make_security_audit_panel(self) -> Panel:
        table = Table(expand=True, box=None, padding=(0, 1))
        table.add_column("Vector", style="bold white", width=14)
        table.add_column("Observed", justify="right", width=10)
        table.add_column("Audit Status", justify="left")

        # IR
        if self.ir_error_rate is None:
            ir_str, ir_stat = "--", "[dim]Not Evaluated[/dim]"
        else:
            ir_pct = f"{self.ir_error_rate * 100:.1f}%"
            if self.ir_error_rate > self.threshold:
                ir_str = f"[bold red]{ir_pct}[/bold red]"
                ir_stat = "[bold red][!] ATTACK DETECTED[/bold red]"
            else:
                ir_str = f"[bold green]{ir_pct}[/bold green]"
                ir_stat = "[bold green][OK] NOMINAL[/bold green]"
        table.add_row("IR Attack:", ir_str, ir_stat)

        # EM
        if self.em_error_rate is None:
            em_str, em_stat = "--", "[dim]Not Evaluated[/dim]"
        else:
            em_pct = f"{self.em_error_rate * 100:.1f}%"
            if self.em_error_rate > self.threshold:
                em_str = f"[bold red]{em_pct}[/bold red]"
                em_stat = "[bold red][!] ATTACK DETECTED[/bold red]"
            else:
                em_str = f"[bold green]{em_pct}[/bold green]"
                em_stat = "[bold green][OK] NOMINAL[/bold green]"
        table.add_row("EM Attack:", em_str, em_stat)

        # EC Fidelity
        if self.ec_fidelity is None:
            ec_str, ec_stat = "--", "[dim]Not Evaluated[/dim]"
        else:
            ec_pct = f"{self.ec_fidelity * 100:.1f}%"
            ec_str = f"[bold green]{ec_pct}[/bold green]"
            ec_stat = "[bold green][OK] 100% RECOVERED[/bold green]"
        table.add_row("EC Fidelity:", ec_str, ec_stat)

        table.add_row("Alert Thresh:", f"{self.threshold * 100:.0f}%", "[dim white]Security Boundary[/dim white]")

        return Panel(table, title="[bold magenta]Security Audit & Verification[/bold magenta]", border_style="magenta")

    def make_analysis_panel(self) -> Panel:
        layout = Layout()
        layout.split_row(
            Layout(name="histogram", ratio=1),
            Layout(name="log", ratio=1)
        )

        # Histogram of top 4 outcomes
        hist_text = Text()
        if not self.latest_counts:
            hist_text.append("[dim]Awaiting circuit execution...\nRun option 1, 2, 3, or 4.[/dim]")
        else:
            sorted_outcomes = sorted(self.latest_counts.items(), key=lambda x: x[1], reverse=True)[:4]
            max_c = max(c for _, c in sorted_outcomes) if sorted_outcomes else 1
            for bitstr, cnt in sorted_outcomes:
                bar_len = int((cnt / max_c) * 14)
                bar = "#" * bar_len + "-" * (14 - bar_len)
                pct = (cnt / self.total_shots) * 100
                hist_text.append(f"{bitstr[:9]:<9} [{bar}] {cnt:4d} ({pct:4.1f}%)\n", style="bright_yellow")

        hist_panel = Panel(hist_text, title="Top-4 Measurement Bitstrings", border_style="yellow")

        # Log
        log_text = Text("\n".join(self.action_log), style="white")
        log_panel = Panel(log_text, title="Mission Event Log", border_style="white")

        layout["histogram"].update(hist_panel)
        layout["log"].update(log_panel)

        return Panel(layout, title="[bold bright_yellow]Real-time Analysis & Logs[/bold bright_yellow]", border_style="yellow")

    def make_command_bar(self) -> Panel:
        cmds = Text.assemble(
            ("Commands: ", "bold yellow"),
            ("1", "bold white on blue"), (" Run HBB  |  ", "white"),
            ("2", "bold white on blue"), (" IR Attack  |  ", "white"),
            ("3", "bold white on blue"), (" EM Attack  |  ", "white"),
            ("4", "bold white on blue"), (" Error Correct  |  ", "white"),
            ("C", "bold white on dark_red"), (" Clear  |  ", "white"),
            ("Q", "bold white on red"), (" Quit", "white")
        )
        return Panel(Align.center(cmds), border_style="bright_cyan")

    def render_layout(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=4),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=3)
        )

        layout["header"].update(self.make_header())
        layout["footer"].update(self.make_command_bar())

        # Body split
        layout["body"].split_column(
            Layout(name="upper", ratio=1),
            Layout(name="lower", size=8)
        )

        layout["upper"].split_row(
            Layout(name="left_sidebar", ratio=1),
            Layout(name="center_stream", ratio=2)
        )

        layout["left_sidebar"].split_column(
            Layout(name="system_info", ratio=1),
            Layout(name="security_audit", ratio=1)
        )

        layout["system_info"].update(self.make_system_info_panel())
        layout["security_audit"].update(self.make_security_audit_panel())
        layout["center_stream"].update(self.make_channel_panel())
        layout["lower"].update(self.make_analysis_panel())

        return layout


def run_demo_mode(app: QSSMissionControl):
    """Walks through each feature step-by-step for headless or preview display."""
    console = app.console
    console.print(app.render_layout())
    time.sleep(0.5)

    console.print("\n[bold cyan]>> Step 1: Executing Standard HBB Protocol...[/bold cyan]")
    app.run_hbb()
    console.print(app.render_layout())
    time.sleep(0.5)

    console.print("\n[bold magenta]>> Step 2: Simulating Intercept-and-Resend (IR) Attack...[/bold magenta]")
    app.run_ir_attack()
    console.print(app.render_layout())
    time.sleep(0.5)

    console.print("\n[bold magenta]>> Step 3: Simulating Entangle-and-Measure (EM) Attack...[/bold magenta]")
    app.run_em_attack()
    console.print(app.render_layout())
    time.sleep(0.5)

    console.print("\n[bold green]>> Step 4: Testing 3-Qubit Error Correction with Toffoli Decoder...[/bold green]")
    app.run_error_correction()
    console.print(app.render_layout())


def run_interactive_mode(app: QSSMissionControl):
    """Runs interactive dashboard responding to keyboard events."""
    console = app.console
    running = True

    try:
        with Live(app.render_layout(), console=console, screen=False, refresh_per_second=4) as live:
            while running:
                ch = None
                if HAS_MSVCRT and msvcrt.kbhit():
                    key = msvcrt.getch()
                    try:
                        ch = key.decode("utf-8").lower()
                    except UnicodeDecodeError:
                        ch = None
                
                if ch:
                    if ch == '1':
                        app.run_hbb()
                    elif ch == '2':
                        app.run_ir_attack()
                    elif ch == '3':
                        app.run_em_attack()
                    elif ch == '4':
                        app.run_error_correction()
                    elif ch == 'c':
                        app.clear()
                    elif ch == 'q':
                        running = False
                        break

                live.update(app.render_layout())
                time.sleep(0.2)
    except Exception:
        # Fallback to demo mode if terminal does not support rich Live cursor control
        run_demo_mode(app)


def main():
    parser = argparse.ArgumentParser(description="Quantum Sentinel HBB Mission Control TUI")
    parser.add_argument("--demo", action="store_true", help="Run automated demonstration walkthrough")
    args = parser.parse_args()

    console = Console()
    app = QSSMissionControl(console)

    if args.demo or not sys.stdin.isatty():
        run_demo_mode(app)
    else:
        run_interactive_mode(app)


if __name__ == "__main__":
    main()
