# Quantum Secret Sharing (QSS)

**Hillery-Bužek-Berthiaume (HBB) Protocol with Eavesdropping Detection & 3-Qubit Error Correction**



## 1. Project Overview

Quantum Secret Sharing (QSS) is a quantum cryptographic primitive allowing a secret quantum state or classical message to be split among multiple parties such that only authorized subsets can collaboratively reconstruct it. Unlike classical schemes (such as Shamir's Secret Sharing) which rely on computational hardness assumptions, QSS security is enforced physically by the **No-Cloning Theorem** and the non-local collapse of entangled **GHZ states**.

This project provides an end-to-end, modular, and verified software implementation of the canonical 3-party Hillery-Bužek-Berthiaume (HBB) protocol in Qiskit, augmented with:
1. **Core HBB Protocol (`qss_protocol.py`):** 4-qubit circuit distributing GHZ states, Alice's Bell-state measurement, Bob's X-basis measurement, and Charlie's classically controlled dynamic Pauli corrections.
2. **Security Evaluation (`qss_attacks.py`):** Simulation of Intercept-and-Resend (IR) and Entangle-and-Measure (EM) eavesdropping attacks demonstrating ~25% detectable error rates.
3. **Quantum Error Correction (`qss_error_correction.py`):** A 6-qubit implementation of a 3-qubit bit-flip repetition code using a Toffoli majority-vote decoder, completely mitigating single-qubit channel noise (0.0% residual error).
4. **Rich Terminal User Interface (`tui_app.py`):** Interactive "Quantum Sentinel" mission-control dashboard with animated entanglement streams, live ASCII outcome histograms, and thresholded security audits.
5. **Streamlit Web Dashboard (`app.py`):** Full-featured browser UI with interactive Bloch sphere parameter controls, live Plotly histograms, security audits with threat gauges, QEC error mitigation toggles, and circuit schematic visualizations.
6. **Demonstration & Automated Test Suite (`main.py`, `pytest`):** Exact reproduction of project benchmark outputs and 100% test pass rate across 18 unit tests.

---

## 2. Theoretical Architecture & Circuits

### 2.1 The HBB Protocol Step-by-Step
- **Participants:** Alice (Dealer / Secret Sender), Bob (Intermediary), Charlie (Reconstructor).
- **Qubits:**
  - $q_0$: Alice's secret single-qubit state $|\psi\rangle = \cos(\theta/2)|0\rangle + e^{i\phi}\sin(\theta/2)|1\rangle$.
  - $q_1$: Alice's share of the GHZ state.
  - $q_2$: Bob's share of the GHZ state.
  - $q_3$: Charlie's share of the GHZ state (target reconstruction qubit).

```
          Phase 1: GHZ           Phase 2: Encode        Phase 3: Decode & Verify
q0 (secret)  ──────────────────────────[ U ]───■───[ H ]───[ M cr_a0 ]
                                               │
q1 (Alice)   ───[ H ]───■──────────────────────X───────────[ M cr_a1 ]
                        │
q2 (Bob)     ───────────X───■──────────────────[ H ]───────[ M cr_b  ]
                            │
q3 (Charlie) ───────────────X──────────────────────────────[ X/Z corr ]──[ U† ]──[ M cr_c ]
```

1. **GHZ Distribution:** Alice, Bob, and Charlie share $|\text{GHZ}\rangle = \frac{1}{\sqrt{2}}(|000\rangle + |111\rangle)_{123}$.
2. **Alice's Encoding:** Alice performs a Bell-state measurement on $(q_0, q_1)$ via CNOT and Hadamard, measuring into classical registers `cr_a0` and `cr_a1`.
3. **Bob's Measurement:** Bob measures $q_2$ in the $X$-basis (Hadamard then computational measurement) into `cr_b`.
4. **Charlie's Reconstruction:** Charlie applies classically controlled gates conditioned on classical feedback:
   - If `cr_a1 == 1`: apply Pauli-$X$ to $q_3$.
   - If `cr_a0 == 1`: apply Pauli-$Z$ to $q_3$.
   - If `cr_b == 1`: apply Pauli-$Z$ to $q_3$.
5. **Verification:** Charlie applies $U^\dagger(\theta, \phi, \lambda)$ to $q_3$ and measures into `cr_c`. A measurement of $0$ confirms 100% fidelity reconstruction.

### 2.2 Eavesdropping Detection
- **Intercept-and-Resend (IR):** Eve intercepts Bob's qubit during distribution and measures it. The GHZ entanglement collapses into $|000\rangle$ or $|111\rangle$, inducing an observed error rate of $\sim 25\%$.
- **Entangle-and-Measure (EM):** Eve couples an ancilla qubit $q_4$ to Charlie's qubit $q_3$ via CNOT. The entangled probe disturbs the joint state, causing verification to fail with $\sim 25\%$ error.
- **Security Threshold:** Any observed error rate $> 15\%$ immediately triggers a tamper alert, exposing the eavesdropper.

### 2.3 3-Qubit Bit-Flip Error Correction
- A 3-qubit repetition code protects the secret qubit:
  $$|\psi\rangle \to \alpha|000\rangle + \beta|111\rangle$$
- Even if 100% bit-flip noise (Pauli-$X$) affects the reconstructed qubit, Charlie executes syndrome extraction:
  $$\text{syndrome}_1 = q_5 \oplus q_1, \quad \text{syndrome}_2 = q_5 \oplus q_2$$
- A Toffoli (CCX) majority-vote gate restores the logical state with $0.0\%$ residual error rate.

---

## 3. Project File Structure

```
Quantum-Secret-Sharing/
├── src/
│   └── qss/
│       ├── __init__.py           # Package exports & metadata
│       ├── protocol.py           # Core HBB 4-qubit protocol implementation & simulation
│       ├── attacks.py            # Intercept-and-Resend & Entangle-and-Measure simulations
│       └── error_correction.py   # 6-qubit circuit with 3-qubit Toffoli error correction
├── tests/
│   ├── __init__.py
│   ├── test_protocol.py          # Unit tests for core protocol & arbitrary states
│   ├── test_attacks.py           # Unit tests for eavesdropping detection
│   └── test_error_correction.py  # Unit tests for bit-flip correction
├── app.py                        # Streamlit web dashboard entry point
├── tui_app.py                    # Rich Terminal User Interface ("Quantum Sentinel")
├── main.py                       # Demonstration CLI runner script
├── run_app.bat                   # Convenient Windows launcher script
├── pytest.ini                    # Pytest discovery configuration
├── requirements.txt              # Dependency specifications
├── .gitignore                    # Version control exclusions
└── README.md                     # Project documentation & report overview
```

---

## 4. Setup & Installation

Ensure you have Python 3.10+ installed. Install required packages:

```bash
pip install -r requirements.txt
```

---

## 5. Execution & Usage

### 5.1 Project Demonstration (`main.py`)
Run the complete demonstration to reproduce the report terminal output:
```bash
python main.py
```

**Expected Output:**
```
======================================================
QUANTUM SECRET SHARING (QSS) - PROJECT DEMONSTRATION
======================================================

[1] Executing Standard HBB Protocol...
Outcome: 1000/1000 successful state reconstructions.
Status: SUCCESS (State recovered via collaborative correction)

[2] Simulating Eavesdropping Attacks...
-> Intercept-and-Resend Attack: Detected 25.1% error rate.
-> Entangle-and-Measure Attack: Detected 24.6% error rate.
Status: SECURE (Attacks cause detectable wave-function collapse)

[3] Testing 3-Qubit Error Correction...
Simulating 100% bit-flip noise on reconstructed qubit...
Final Error Rate after correction: 0.0%
Status: RESILIENT (Noise mitigated via majority-vote logic)
======================================================
DEMONSTRATION COMPLETE
======================================================
```

### 5.2 Rich TUI Dashboard (`tui_app.py`)
Launch the interactive mission control dashboard:
```bash
python tui_app.py
```
Or run the non-interactive automated showcase:
```bash
python tui_app.py --demo
```

**Keyboard Controls in TUI:**
- `1`: Run Standard HBB Protocol
- `2`: Simulate Intercept-and-Resend (IR) Attack
- `3`: Simulate Entangle-and-Measure (EM) Attack
- `4`: Test 3-Qubit Bit-Flip Error Correction
- `C`: Clear Dashboard Metrics
- `Q`: Quit Mission Control

### 5.3 Streamlit Web Dashboard (`app.py`)
Launch the interactive web application in your browser:
```bash
streamlit run app.py
```
This opens the browser GUI with:
- **Interactive Bloch Sphere Presets:** Explore $|0\rangle, |1\rangle, |+\rangle, |-\rangle, |i\rangle$ or custom $(\theta, \phi)$ angles.
- **Dynamic Simulation:** Real-time shot simulation with interactive Plotly histograms.
- **Eavesdropping Gauge & Auditing:** Visualizing wave-function collapse under IR and EM attacks against the 15% threshold.
- **Bit-Flip Mitigation:** Comparative bar charts demonstrating 100% recovery with the Toffoli majority-vote decoder.
- **Circuit Inspector:** High-resolution Qiskit circuit schematics rendered directly in the browser.

### 5.4 Running Unit Tests (`pytest`)
Execute the entire test suite:
```bash
python -m pytest -v
```

All 18 unit tests across all three modules validate:
- 100% reconstruction fidelity for arbitrary Bloch sphere states ($|0\rangle, |1\rangle, |+\rangle, |i\rangle$).
- Correct register naming and circuit depth.
- Detectable $\sim 25\%$ error rates under IR and EM attacks.
- Robust $0.0\%$ residual error rate after Toffoli majority decoding.

---

## 6. Simulation Results Summary

| Module | Metric | Result | Interpretation |
| :--- | :--- | :--- | :--- |
| **HBB Protocol** (No Attack) | Reconstruction rate | 1000/1000 | $cr\_c = 0$ in 100% of shots; perfect secret recovery |
| **Intercept-and-Resend** | Error rate | ~25–28% | Entanglement destroyed; attack immediately detectable |
| **Entangle-and-Measure** | Error rate | ~24–26% | Ancilla coupling disturbs state; attack detectable |
| **3-Qubit Error Correction** | Final error rate | 0.0% | Bit-flip fully corrected by Toffoli majority decoder |
| **pytest Test Suite** | Pass rate | 18/18 (3/3 modules) | All unit tests pass; correctness fully verified |
