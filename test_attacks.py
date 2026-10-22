"""
Unit Tests for Security Attack Simulations (qss_attacks.py)
"""

import numpy as np
import pytest
from qss_attacks import (
    create_intercept_resend_circuit,
    create_entangle_measure_circuit,
    simulate_intercept_resend,
    simulate_entangle_measure,
    calculate_attack_error_rate
)


def test_ir_circuit_structure():
    """Verify registers and qubit counts for Intercept-and-Resend circuit."""
    qc = create_intercept_resend_circuit()
    assert qc.num_qubits == 4
    assert qc.num_clbits == 5
    reg_names = [r.name for r in qc.cregs]
    assert "cr_eve" in reg_names
    assert "cr_c" in reg_names


def test_em_circuit_structure():
    """Verify registers and qubit counts for Entangle-and-Measure circuit."""
    qc = create_entangle_measure_circuit()
    assert qc.num_qubits == 5  # Includes Eve's ancilla qr[4]
    assert qc.num_clbits == 5
    reg_names = [r.name for r in qc.cregs]
    assert "cr_eve" in reg_names
    assert "cr_c" in reg_names


def test_ir_attack_detectable_disturbance():
    """Verify that Intercept-and-Resend attack induces detectable error rate (~25%)."""
    counts, err_rate = simulate_intercept_resend(shots=1500)
    assert 0.18 <= err_rate <= 0.32, f"IR Error rate {err_rate:.3f} outside expected range [0.18, 0.32]"
    # Must comfortably exceed the security alert threshold of 15%
    assert err_rate > 0.15


def test_em_attack_detectable_disturbance():
    """Verify that Entangle-and-Measure attack induces detectable error rate (~25%)."""
    counts, err_rate = simulate_entangle_measure(shots=1500)
    assert 0.18 <= err_rate <= 0.32, f"EM Error rate {err_rate:.3f} outside expected range [0.18, 0.32]"
    # Must comfortably exceed the security alert threshold of 15%
    assert err_rate > 0.15


def test_calculate_attack_error_rate_helper():
    """Verify attack error rate parser with synthetic bitstrings."""
    # Format: cr_eve cr_c cr_b cr_a1 cr_a0
    synthetic = {
        "0 1 0 0 0": 25,  # cr_c = 1 (error)
        "1 1 0 1 0": 25,  # cr_c = 1 (error)
        "0 0 0 0 0": 25,  # cr_c = 0 (success)
        "1 0 1 1 1": 25,  # cr_c = 0 (success)
    }
    errs, total, rate = calculate_attack_error_rate(synthetic)
    assert errs == 50
    assert total == 100
    assert rate == 0.5
