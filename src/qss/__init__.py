"""
Quantum Secret Sharing (QSS) Package
====================================
Hillery-Bužek-Berthiaume (HBB) Protocol with Eavesdropping Detection
and 3-Qubit Bit-Flip Quantum Error Correction.
"""

from .protocol import create_qss_circuit, simulate_qss, parse_qss_counts
from .attacks import (
    create_intercept_resend_circuit,
    create_entangle_measure_circuit,
    simulate_intercept_resend,
    simulate_entangle_measure,
    calculate_attack_error_rate
)
from .error_correction import (
    create_qss_error_correction_circuit,
    simulate_qss_error_correction,
    calculate_ec_error_rate
)

__version__ = "1.0.0"
__author__ = "Vishal Acharya"

__all__ = [
    "create_qss_circuit",
    "simulate_qss",
    "parse_qss_counts",
    "create_intercept_resend_circuit",
    "create_entangle_measure_circuit",
    "simulate_intercept_resend",
    "simulate_entangle_measure",
    "calculate_attack_error_rate",
    "create_qss_error_correction_circuit",
    "simulate_qss_error_correction",
    "calculate_ec_error_rate"
]
