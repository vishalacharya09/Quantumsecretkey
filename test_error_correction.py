"""
Unit Tests for 3-Qubit Bit-Flip Error Correction (qss_error_correction.py)
"""

import numpy as np
import pytest
from qss_error_correction import (
    create_qss_error_correction_circuit,
    simulate_qss_error_correction,
    calculate_ec_error_rate
)


def test_error_correction_circuit_structure():
    """Verify registers and qubit counts for the 6-qubit error correction circuit."""
    qc = create_qss_error_correction_circuit()
    assert qc.num_qubits == 6, f"Expected 6 qubits, got {qc.num_qubits}"
    assert qc.num_clbits == 4, f"Expected 4 classical bits, got {qc.num_clbits}"
    reg_names = [r.name for r in qc.cregs]
    assert "cr_a0" in reg_names
    assert "cr_a1" in reg_names
    assert "cr_b" in reg_names
    assert "cr_c" in reg_names


def test_bit_flip_correction_reconstructed_qubit():
    """Verify that Toffoli majority-vote decoder corrects 100% of bit-flip noise on q5."""
    # With correction: error rate must be 0.0%
    counts, err_rate = simulate_qss_error_correction(
        inject_bit_flip=True,
        error_qubit=5,
        apply_correction=True,
        shots=1000
    )
    assert err_rate == 0.0, f"Expected 0.0 error rate with correction, got {err_rate}"

    # Without correction: error rate must be significantly elevated
    counts_uncorrected, raw_err = simulate_qss_error_correction(
        inject_bit_flip=True,
        error_qubit=5,
        apply_correction=False,
        shots=1000
    )
    assert raw_err > 0.5, f"Expected elevated error rate without correction, got {raw_err}"


def test_bit_flip_on_ancilla_qubits():
    """Verify that bit flips on physical code ancilla qubits (q1, q2) are also tolerated."""
    for q in (1, 2):
        counts, err_rate = simulate_qss_error_correction(
            inject_bit_flip=True,
            error_qubit=q,
            apply_correction=True,
            shots=500
        )
        assert err_rate == 0.0, f"Error correction failed for bit flip on qubit {q}"


def test_no_noise_baseline():
    """Verify that the circuit without noise preserves 100% fidelity."""
    counts, err_rate = simulate_qss_error_correction(
        inject_bit_flip=False,
        apply_correction=True,
        shots=500
    )
    assert err_rate == 0.0


def test_calculate_ec_error_rate_helper():
    """Verify helper with synthetic counts."""
    # Format: cr_c cr_b cr_a1 cr_a0
    synthetic = {
        "0 0 0 0": 80,  # cr_c = 0 (success)
        "1 0 0 0": 20,  # cr_c = 1 (error)
    }
    errs, total, rate = calculate_ec_error_rate(synthetic)
    assert errs == 20
    assert total == 100
    assert rate == 0.2
