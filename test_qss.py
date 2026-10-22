"""
Unit Tests for Core HBB Quantum Secret Sharing Protocol (qss_protocol.py)
"""

import numpy as np
import pytest
from qss_protocol import create_qss_circuit, simulate_qss, parse_qss_counts


def test_circuit_structure():
    """Verify that the HBB circuit has the exact required registers and qubits."""
    qc = create_qss_circuit()
    assert qc.num_qubits == 4, f"Expected 4 qubits, got {qc.num_qubits}"
    assert qc.num_clbits == 4, f"Expected 4 classical bits, got {qc.num_clbits}"
    reg_names = [r.name for r in qc.cregs]
    assert "cr_a0" in reg_names
    assert "cr_a1" in reg_names
    assert "cr_b" in reg_names
    assert "cr_c" in reg_names


def test_standard_hbb_reconstruction():
    """Verify 100% reconstruction success under ideal conditions."""
    counts = simulate_qss(theta=np.pi / 3, phi=np.pi / 4, shots=1000)
    success, total, rate = parse_qss_counts(counts)
    assert total == 1000
    assert success == 1000, f"Expected 1000 successful shots, got {success}"
    assert rate == 1.0


@pytest.mark.parametrize("theta,phi", [
    (0.0, 0.0),                  # |0>
    (np.pi, 0.0),                # |1>
    (np.pi / 2, 0.0),            # |+>
    (np.pi / 2, np.pi / 2),      # |i>
    (np.pi / 4, np.pi / 3),      # arbitrary superposition
])
def test_arbitrary_quantum_states(theta, phi):
    """Verify that any arbitrary secret state is faithfully reconstructed."""
    counts = simulate_qss(theta=theta, phi=phi, shots=500)
    success, total, rate = parse_qss_counts(counts)
    assert success == total
    assert rate == 1.0


def test_parse_counts_edge_cases():
    """Test parse helper with synthetic counts."""
    synthetic = {"0 0 0 0": 50, "1 0 0 0": 50}
    success, total, rate = parse_qss_counts(synthetic)
    assert success == 50
    assert total == 100
    assert rate == 0.5
