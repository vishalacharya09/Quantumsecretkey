"""
Quantum Secret Sharing (QSS) - Security Attack Simulations
Simulations of canonical eavesdropping strategies against the HBB protocol:
1. Intercept-and-Resend (IR) Attack:
   Eve intercepts Bob's GHZ qubit during distribution, measures it in the computational
   basis, and re-injects the collapsed qubit. Entanglement is destroyed.
2. Entangle-and-Measure (EM) Attack:
   Eve introduces an ancilla qubit and entangles it with Charlie's GHZ qubit via CNOT.
   Eve later measures her ancilla to extract correlated information.
   
Both attacks disturb the quantum state, inducing a statistically detectable ~25% error
rate in verification, confirming quantum unconditional security (No-Cloning Theorem).
"""

from typing import Dict, Tuple
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator


def create_intercept_resend_circuit(
    theta: float = np.pi / 4,
    phi: float = np.pi / 4,
    lambda_param: float = 0.0
) -> QuantumCircuit:
    """
    Constructs an HBB circuit under an Intercept-and-Resend (IR) attack by Eve.
    
    Eve intercepts Bob's GHZ qubit qr[2] after preparation, measuring it into cr_eve.
    """
    qr = QuantumRegister(4, 'q')
    cr_a0 = ClassicalRegister(1, 'cr_a0')
    cr_a1 = ClassicalRegister(1, 'cr_a1')
    cr_b = ClassicalRegister(1, 'cr_b')
    cr_c = ClassicalRegister(1, 'cr_c')
    cr_eve = ClassicalRegister(1, 'cr_eve')
    qc = QuantumCircuit(qr, cr_a0, cr_a1, cr_b, cr_c, cr_eve)

    # Phase 1: GHZ State Preparation
    qc.h(qr[1])
    qc.cx(qr[1], qr[2])
    qc.cx(qr[2], qr[3])
    qc.barrier()

    # Eavesdropping: Eve intercepts and measures Bob's qubit qr[2]
    qc.measure(qr[2], cr_eve[0])  # Entanglement destroyed; qr[2] collapses to |0> or |1>
    qc.barrier()

    # Phase 2: Alice encodes the secret qubit
    qc.u(theta, phi, lambda_param, qr[0])
    qc.cx(qr[0], qr[1])
    qc.h(qr[0])
    qc.measure(qr[0], cr_a0[0])
    qc.measure(qr[1], cr_a1[0])
    qc.barrier()

    # Phase 3: Bob measures in X-basis
    qc.h(qr[2])
    qc.measure(qr[2], cr_b[0])

    # Charlie applies classically-controlled corrections
    with qc.if_test((cr_a1, 1)):
        qc.x(qr[3])
    with qc.if_test((cr_a0, 1)):
        qc.z(qr[3])
    with qc.if_test((cr_b, 1)):
        qc.z(qr[3])
    qc.barrier()

    # Verification: Inverse unitary and measurement into cr_c
    qc.u(-theta, -lambda_param, -phi, qr[3])
    qc.measure(qr[3], cr_c[0])

    return qc


def create_entangle_measure_circuit(
    theta: float = np.pi / 4,
    phi: float = np.pi / 4,
    lambda_param: float = 0.0
) -> QuantumCircuit:
    """
    Constructs an HBB circuit under an Entangle-and-Measure (EM) attack by Eve.
    
    Eve introduces a 5th ancilla qubit qr[4] and couples it to Charlie's GHZ qubit qr[3].
    Eve later measures qr[4] into cr_eve.
    """
    qr = QuantumRegister(5, 'q')  # qr[4] is Eve's ancilla
    cr_a0 = ClassicalRegister(1, 'cr_a0')
    cr_a1 = ClassicalRegister(1, 'cr_a1')
    cr_b = ClassicalRegister(1, 'cr_b')
    cr_c = ClassicalRegister(1, 'cr_c')
    cr_eve = ClassicalRegister(1, 'cr_eve')
    qc = QuantumCircuit(qr, cr_a0, cr_a1, cr_b, cr_c, cr_eve)

    # Phase 1: GHZ State Preparation
    qc.h(qr[1])
    qc.cx(qr[1], qr[2])
    qc.cx(qr[2], qr[3])
    qc.barrier()

    # Eavesdropping: Eve couples her ancilla to Charlie's qubit
    qc.cx(qr[3], qr[4])
    qc.barrier()

    # Phase 2: Alice encodes secret
    qc.u(theta, phi, lambda_param, qr[0])
    qc.cx(qr[0], qr[1])
    qc.h(qr[0])
    qc.measure(qr[0], cr_a0[0])
    qc.measure(qr[1], cr_a1[0])
    qc.barrier()

    # Phase 3: Bob measures in X-basis
    qc.h(qr[2])
    qc.measure(qr[2], cr_b[0])

    # Charlie applies classically-controlled corrections
    with qc.if_test((cr_a1, 1)):
        qc.x(qr[3])
    with qc.if_test((cr_a0, 1)):
        qc.z(qr[3])
    with qc.if_test((cr_b, 1)):
        qc.z(qr[3])
    qc.barrier()

    # Eve measures her ancilla to extract correlated state information
    qc.measure(qr[4], cr_eve[0])

    # Verification: Inverse unitary and measurement into cr_c
    qc.u(-theta, -lambda_param, -phi, qr[3])
    qc.measure(qr[3], cr_c[0])

    return qc


def calculate_attack_error_rate(counts: Dict[str, int]) -> Tuple[int, int, float]:
    """
    Calculates the error rate induced by eavesdropping.
    
    In both IR and EM circuits:
        Register list: [qr, cr_a0, cr_a1, cr_b, cr_c, cr_eve]
        Bitstring representation: "cr_eve cr_c cr_b cr_a1 cr_a0"
        cr_c is index 1 from left in space-separated tokens.
        cr_c == '1' indicates a failed verification (eavesdropping error).

    Returns:
        Tuple of (error_shots, total_shots, error_rate)
    """
    total_shots = sum(counts.values())
    error_shots = 0

    for bitstring, count in counts.items():
        tokens = bitstring.split()
        if len(tokens) >= 2:
            cr_c_val = tokens[1]
        else:
            # Fallback if unseparated
            cr_c_val = bitstring[1] if len(bitstring) > 1 else bitstring[0]
            
        if cr_c_val == '1':
            error_shots += count

    error_rate = (error_shots / total_shots) if total_shots > 0 else 0.0
    return error_shots, total_shots, error_rate


def simulate_intercept_resend(
    theta: float = np.pi / 4,
    phi: float = np.pi / 4,
    lambda_param: float = 0.0,
    shots: int = 1000
) -> Tuple[Dict[str, int], float]:
    """
    Simulates the Intercept-and-Resend attack and returns counts and error rate.
    """
    qc = create_intercept_resend_circuit(theta, phi, lambda_param)
    sim = AerSimulator()
    counts = sim.run(qc, shots=shots).result().get_counts()
    _, _, err_rate = calculate_attack_error_rate(counts)
    return counts, err_rate


def simulate_entangle_measure(
    theta: float = np.pi / 4,
    phi: float = np.pi / 4,
    lambda_param: float = 0.0,
    shots: int = 1000
) -> Tuple[Dict[str, int], float]:
    """
    Simulates the Entangle-and-Measure attack and returns counts and error rate.
    """
    qc = create_entangle_measure_circuit(theta, phi, lambda_param)
    sim = AerSimulator()
    counts = sim.run(qc, shots=shots).result().get_counts()
    _, _, err_rate = calculate_attack_error_rate(counts)
    return counts, err_rate


if __name__ == '__main__':
    print("=" * 60)
    print("Quantum Secret Sharing - Security Attack Simulations")
    print("=" * 60)

    print("\n[1] Running Intercept-and-Resend (IR) Attack...")
    ir_counts, ir_err = simulate_intercept_resend(shots=1000)
    print(f" -> IR Error Rate: {ir_err * 100:.1f}%")
    print(f" -> Threshold: 15.0% | Status: {'DETECTED (SECURE)' if ir_err > 0.15 else 'UNDETECTED'}")

    print("\n[2] Running Entangle-and-Measure (EM) Attack...")
    em_counts, em_err = simulate_entangle_measure(shots=1000)
    print(f" -> EM Error Rate: {em_err * 100:.1f}%")
    print(f" -> Threshold: 15.0% | Status: {'DETECTED (SECURE)' if em_err > 0.15 else 'UNDETECTED'}")
