"""
Quantum Secret Sharing (QSS) - Core HBB Protocol
================================================
Implementation of the Hillery-Bužek-Berthiaume (HBB) 3-party protocol.

Alice (secret sender) distributes a GHZ-entangled state among Alice, Bob, and Charlie.
Alice encodes a secret single-qubit state via Bell-state measurement.
Bob measures his qubit in the X-basis.
Charlie receives classical measurement bits from Alice and Bob and applies conditional
unitary Pauli corrections to perfectly reconstruct the secret qubit.
"""

from typing import Dict, Tuple
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator


def create_qss_circuit(
    theta: float = np.pi / 3,
    phi: float = np.pi / 4,
    lambda_param: float = 0.0
) -> QuantumCircuit:
    """
    Constructs the 4-qubit HBB Quantum Secret Sharing circuit with verification.

    Qubits:
        qr[0]: Alice's secret qubit |psi>
        qr[1]: Alice's share of the GHZ state
        qr[2]: Bob's share of the GHZ state
        qr[3]: Charlie's share of the GHZ state (reconstruction target)

    Classical Registers:
        cr_a0: Alice's measurement of qr[0] (Bell basis)
        cr_a1: Alice's measurement of qr[1] (Bell basis)
        cr_b:  Bob's measurement of qr[2] (X basis)
        cr_c:  Verification measurement of qr[3] (after inverse U)
    """
    qr = QuantumRegister(4, 'q')
    cr_a0 = ClassicalRegister(1, 'cr_a0')
    cr_a1 = ClassicalRegister(1, 'cr_a1')
    cr_b = ClassicalRegister(1, 'cr_b')
    cr_c = ClassicalRegister(1, 'cr_c')
    qc = QuantumCircuit(qr, cr_a0, cr_a1, cr_b, cr_c)

    # Phase 1: GHZ State Preparation (|000> + |111>) / sqrt(2) on qr[1, 2, 3]
    qc.h(qr[1])
    qc.cx(qr[1], qr[2])
    qc.cx(qr[2], qr[3])
    qc.barrier()

    # Phase 2: Alice encodes the secret state U(theta, phi, lambda)|0>
    qc.u(theta, phi, lambda_param, qr[0])  # Secret qubit preparation
    qc.cx(qr[0], qr[1])                    # Bell-state measurement step 1
    qc.h(qr[0])                            # Bell-state measurement step 2
    qc.measure(qr[0], cr_a0[0])
    qc.measure(qr[1], cr_a1[0])
    qc.barrier()

    # Phase 3: Bob measures in X-basis
    qc.h(qr[2])
    qc.measure(qr[2], cr_b[0])

    # Charlie applies classically-controlled corrections based on (cr_a0, cr_a1, cr_b)
    # If cr_a1 == 1, apply Pauli-X
    with qc.if_test((cr_a1, 1)):
        qc.x(qr[3])
    # If cr_a0 == 1, apply Pauli-Z
    with qc.if_test((cr_a0, 1)):
        qc.z(qr[3])
    # If cr_b == 1, apply Pauli-Z
    with qc.if_test((cr_b, 1)):
        qc.z(qr[3])
    qc.barrier()

    # Verification: Apply inverse unitary U^dagger and measure into cr_c
    # U(theta, phi, lambda)^dagger = U(-theta, -lambda, -phi)
    qc.u(-theta, -lambda_param, -phi, qr[3])
    qc.measure(qr[3], cr_c[0])

    return qc


def simulate_qss(
    theta: float = np.pi / 3,
    phi: float = np.pi / 4,
    lambda_param: float = 0.0,
    shots: int = 1000
) -> Dict[str, int]:
    """
    Simulates the HBB QSS circuit using the Qiskit-Aer simulator.

    Returns:
        Dict[str, int]: Bitstring measurement outcome counts.
    """
    qc = create_qss_circuit(theta, phi, lambda_param)
    simulator = AerSimulator()
    result = simulator.run(qc, shots=shots).result()
    return result.get_counts()


def parse_qss_counts(counts: Dict[str, int]) -> Tuple[int, int, float]:
    """
    Parses simulation counts to extract the verification bit cr_c.

    In Qiskit's multi-register string representation:
        String format: "cr_c cr_b cr_a1 cr_a0"
        cr_c is the leftmost space-separated token.

    Returns:
        Tuple of (successful_shots, total_shots, reconstruction_rate)
    """
    total_shots = sum(counts.values())
    successful_shots = 0

    for bitstring, count in counts.items():
        tokens = bitstring.split()
        cr_c_val = tokens[0] if tokens else bitstring[0]
        if cr_c_val == '0':
            successful_shots += count

    rate = (successful_shots / total_shots) if total_shots > 0 else 0.0
    return successful_shots, total_shots, rate


if __name__ == '__main__':
    print("=" * 60)
    print("Quantum Secret Sharing (HBB Protocol) Simulation")
    print("=" * 60)
    theta_val = np.pi / 3
    phi_val = np.pi / 4
    shots_num = 1000

    qc_instance = create_qss_circuit(theta_val, phi_val)
    print("Circuit Summary:")
    print(f" - Qubits: {qc_instance.num_qubits}")
    print(f" - Classical bits: {qc_instance.num_clbits}")
    print(f" - Depth: {qc_instance.depth()}")

    raw_counts = simulate_qss(theta_val, phi_val, shots=shots_num)
    success, total, success_rate = parse_qss_counts(raw_counts)

    print(f"Outcome: {success}/{total} successful state reconstructions.")
    print(f"Success Rate: {success_rate * 100:.1f}%")
    print(f"Status: {'SUCCESS' if success_rate == 1.0 else 'FAILED'}")
