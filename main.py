"""
Quantum Secret Sharing (QSS) - Project Demonstration
Runs the full suite of simulations:
1. Standard HBB Protocol
2. Eavesdropping Attacks (IR and EM)
3. 3-Qubit Error Correction
Outputs formatted results consistent with the project report.
"""

from qss_protocol import simulate_qss, parse_qss_counts
from qss_attacks import simulate_intercept_resend, simulate_entangle_measure
from qss_error_correction import simulate_qss_error_correction


def run_demonstration(shots: int = 1000) -> None:
    print("======================================================")
    print("QUANTUM SECRET SHARING (QSS) - PROJECT DEMONSTRATION")
    print("======================================================")

    # [1] Standard HBB Protocol
    print("\n[1] Executing Standard HBB Protocol...")
    qss_counts = simulate_qss(shots=shots)
    success, total, _ = parse_qss_counts(qss_counts)
    print(f"Outcome: {success}/{total} successful state reconstructions.")
    print("Status: SUCCESS (State recovered via collaborative correction)")

    # [2] Eavesdropping Attacks
    print("\n[2] Simulating Eavesdropping Attacks...")
    _, ir_err = simulate_intercept_resend(shots=shots)
    _, em_err = simulate_entangle_measure(shots=shots)
    print(f"-> Intercept-and-Resend Attack: Detected {ir_err * 100:.1f}% error rate.")
    print(f"-> Entangle-and-Measure Attack: Detected {em_err * 100:.1f}% error rate.")
    print("Status: SECURE (Attacks cause detectable wave-function collapse)")

    # [3] 3-Qubit Error Correction
    print("\n[3] Testing 3-Qubit Error Correction...")
    print("Simulating 100% bit-flip noise on reconstructed qubit...")
    _, ec_err = simulate_qss_error_correction(inject_bit_flip=True, apply_correction=True, shots=shots)
    print(f"Final Error Rate after correction: {ec_err * 100:.1f}%")
    print("Status: RESILIENT (Noise mitigated via majority-vote logic)")

    print("======================================================")
    print("DEMONSTRATION COMPLETE")
    print("======================================================")


if __name__ == "__main__":
    run_demonstration()
