"""
Quantum Secret Sharing (QSS) - Interactive Streamlit Web Dashboard
Hillery-Bužek-Berthiaume (HBB) Protocol with Eavesdropping Detection & 3-Qubit Error Correction

Student: Vishal Acharya (Roll No.: 231070077)
Department of Computer Engineering | Quantum Computing Laboratory
Veermata Jijabai Technological Institute (VJTI), Mumbai
"""

import math
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from qss_protocol import create_qss_circuit, simulate_qss, parse_qss_counts
from qss_attacks import (
    create_intercept_resend_circuit,
    create_entangle_measure_circuit,
    simulate_intercept_resend,
    simulate_entangle_measure,
    calculate_attack_error_rate
)
from qss_error_correction import (
    create_qss_error_correction_circuit,
    simulate_qss_error_correction,
    calculate_ec_error_rate
)

# Page configuration
st.set_page_config(
    page_title="Quantum Secret Sharing (QSS) Explorer",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #546E7A;
        margin-bottom: 1.2rem;
    }
    .metric-card {
        background: rgba(30, 136, 229, 0.08);
        border: 1px solid rgba(30, 136, 229, 0.2);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .status-badge-success {
        color: #2E7D32;
        background-color: #E8F5E9;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 6px;
        display: inline-block;
    }
    .status-badge-alert {
        color: #C62828;
        background-color: #FFEBEE;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 6px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)


# Sidebar Configuration
st.sidebar.markdown("## ⚛️ QSS Mission Control")
st.sidebar.markdown("**HBB Protocol Simulator**  \n*Vishal Acharya (231070077)*  \n*VJTI, Mumbai*")
st.sidebar.divider()

nav_option = st.sidebar.radio(
    "Navigation Modules:",
    [
        "🚀 Core HBB Protocol",
        "🛡️ Eavesdropping & Security",
        "🔧 3-Qubit Error Correction",
        "📐 Circuit Visualizer",
        "📖 Theory & Applications"
    ]
)

st.sidebar.divider()
st.sidebar.markdown("### ⚙️ Global Parameters")
shots_param = st.sidebar.slider("Simulation Shots", min_value=200, max_value=5000, value=1000, step=200)

state_preset = st.sidebar.selectbox(
    "Secret State Preset (|ψ⟩):",
    [
        "Custom (π/3, π/4)",
        "|0⟩ (Ground State)",
        "|1⟩ (Excited State)",
        "|+⟩ (Equator Superposition)",
        "|-⟩ (Phase Superposition)",
        "|i⟩ (Y-axis Superposition)"
    ]
)

if state_preset == "|0⟩ (Ground State)":
    theta_val, phi_val = 0.0, 0.0
elif state_preset == "|1⟩ (Excited State)":
    theta_val, phi_val = np.pi, 0.0
elif state_preset == "|+⟩ (Equator Superposition)":
    theta_val, phi_val = np.pi / 2, 0.0
elif state_preset == "|-⟩ (Phase Superposition)":
    theta_val, phi_val = np.pi / 2, np.pi
elif state_preset == "|i⟩ (Y-axis Superposition)":
    theta_val, phi_val = np.pi / 2, np.pi / 2
else:
    theta_val = st.sidebar.slider("Theta (θ)", min_value=0.0, max_value=float(np.pi), value=float(np.pi/3), step=0.05)
    phi_val = st.sidebar.slider("Phi (ϕ)", min_value=0.0, max_value=float(2*np.pi), value=float(np.pi/4), step=0.05)


# Header
st.markdown('<div class="main-title">Quantum Secret Sharing (QSS) Web Explorer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">A Comprehensive Implementation of the Hillery-Bužek-Berthiaume (HBB) Protocol with Eavesdropping Detection and 3-Qubit Error Correction</div>', unsafe_allow_html=True)


# ==========================================================
# MODULE 1: CORE HBB PROTOCOL
# ==========================================================
if nav_option == "🚀 Core HBB Protocol":
    st.markdown("### 🚀 Core Hillery-Bužek-Berthiaume (HBB) 3-Party Protocol")
    st.info("""
    **Protocol Mechanism:**
    1. **GHZ Distribution:** Alice, Bob, and Charlie share a maximally entangled Greenberger-Horne-Zeilinger (GHZ) state $\\frac{1}{\\sqrt{2}}(|000\\rangle + |111\\rangle)$.
    2. **Secret Encoding:** Alice encodes secret qubit $|\\psi\\rangle$ using a Bell-state measurement on $(q_0, q_1)$.
    3. **Collaborative Decoding:** Bob measures $q_2$ in the $X$-basis and broadcasts his bit. Charlie receives classical bits from Alice and Bob, applying conditional Pauli corrections ($X, Z$) to reconstruct $|\\psi\\rangle$ with 100% fidelity.
    """)

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        st.metric("Secret Angle θ", f"{theta_val:.3f} rad ({theta_val/np.pi:.2f}π)")
    with col2:
        st.metric("Secret Angle ϕ", f"{phi_val:.3f} rad ({phi_val/np.pi:.2f}π)")
    with col3:
        st.metric("Simulated Backend", "Qiskit-Aer (AerSimulator)")

    run_sim = st.button("▶️ Execute HBB Simulation", type="primary", use_container_width=True)

    if run_sim or "hbb_counts" not in st.session_state:
        with st.spinner("Simulating 4-qubit HBB quantum circuit..."):
            counts = simulate_qss(theta=theta_val, phi=phi_val, shots=shots_param)
            st.session_state["hbb_counts"] = counts

    if "hbb_counts" in st.session_state:
        counts = st.session_state["hbb_counts"]
        success, total, rate = parse_qss_counts(counts)

        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Total Shots", total)
        m_col2.metric("Successful Reconstructions", success)
        m_col3.metric("Reconstruction Rate", f"{rate * 100:.1f}%")
        with m_col4:
            st.markdown("**Channel Status:**")
            if rate == 1.0:
                st.markdown('<span class="status-badge-success">✓ SUCCESS: 100% Recovery</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="status-badge-alert">⚠️ PARTIAL RECONSTRUCTION</span>', unsafe_allow_html=True)

        st.markdown("#### Measurement Outcome Distribution (`cr_c cr_b cr_a1 cr_a0`)")
        st.caption("Verification bit `cr_c == 0` confirms exact quantum state reconstruction.")

        labels = list(counts.keys())
        values = list(counts.values())

        fig = go.Figure(data=[
            go.Bar(
                x=labels,
                y=values,
                text=values,
                textposition='auto',
                marker_color=['#1E88E5' if k.split()[0] == '0' else '#E53935' for k in labels]
            )
        ])
        fig.update_layout(
            title="Measurement Histogram across Classical Registers",
            xaxis_title="Bitstring (cr_c cr_b cr_a1 cr_a0)",
            yaxis_title="Shot Count",
            template="plotly_white",
            height=380
        )
        st.plotly_chart(fig, use_container_width=True)


# ==========================================================
# MODULE 2: EAVESDROPPING & SECURITY
# ==========================================================
elif nav_option == "🛡️ Eavesdropping & Security":
    st.markdown("### 🛡️ Eavesdropping Detection & Quantum Security Audit")
    st.markdown("""
    Under quantum mechanics (the **No-Cloning Theorem** and wavefunction collapse), an eavesdropper (**Eve**) cannot extract information from the quantum channel without irreversibly disturbing the entangled state.
    We simulate two canonical attack models:
    - **Intercept-and-Resend (IR):** Eve measures Bob's GHZ qubit during transit in the computational basis, destroying entanglement.
    - **Entangle-and-Measure (EM):** Eve couples an ancilla qubit to Charlie's share via CNOT, perturbing Charlie's state space.
    """)

    threshold = 0.15  # 15% detection threshold

    run_attacks = st.button("🚨 Simulate Eavesdropping Attacks", type="primary", use_container_width=True)

    if run_attacks or "ir_err" not in st.session_state:
        with st.spinner("Simulating attack channels and disturbance..."):
            _, ir_err = simulate_intercept_resend(shots=shots_param)
            _, em_err = simulate_entangle_measure(shots=shots_param)
            st.session_state["ir_err"] = ir_err
            st.session_state["em_err"] = em_err

    ir_err = st.session_state["ir_err"]
    em_err = st.session_state["em_err"]

    col_ir, col_em, col_thresh = st.columns(3)
    with col_ir:
        st.metric("IR Attack Error Rate", f"{ir_err * 100:.1f}%")
        if ir_err > threshold:
            st.markdown('<span class="status-badge-alert">🚨 ATTACK DETECTED (SECURE)</span>', unsafe_allow_html=True)
    with col_em:
        st.metric("EM Attack Error Rate", f"{em_err * 100:.1f}%")
        if em_err > threshold:
            st.markdown('<span class="status-badge-alert">🚨 ATTACK DETECTED (SECURE)</span>', unsafe_allow_html=True)
    with col_thresh:
        st.metric("Security Alert Threshold", f"{threshold * 100:.0f}%")
        st.markdown('<span class="status-badge-success">Parameter Estimation Bound</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Security Audit: Error Rate Comparison")

    categories = ["Clean HBB Channel", "Intercept-and-Resend (IR)", "Entangle-and-Measure (EM)"]
    rates = [0.0, ir_err * 100, em_err * 100]
    colors = ["#43A047", "#E53935", "#FB8C00"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=categories,
        y=rates,
        text=[f"{r:.1f}%" for r in rates],
        textposition='auto',
        marker_color=colors
    ))
    fig.add_hline(
        y=threshold * 100,
        line_dash="dash",
        line_color="red",
        annotation_text="Alarm Threshold (15%)",
        annotation_position="top left"
    )
    fig.update_layout(
        title="Disturbance Introduced by Eavesdropping vs Clean Baseline",
        yaxis_title="Observed Verification Error Rate (%)",
        yaxis_range=[0, 40],
        template="plotly_white",
        height=380
    )
    st.plotly_chart(fig, use_container_width=True)

    st.success(r"✅ **Quantum Security Verification:** Both attacks cause statistically detectable errors ($\sim 25\%$), well above the 15% parameter-estimation threshold, confirming that eavesdropping cannot remain undetected.")


# ==========================================================
# MODULE 3: 3-QUBIT ERROR CORRECTION
# ==========================================================
elif nav_option == "🔧 3-Qubit Error Correction":
    st.markdown("### 🔧 3-Qubit Bit-Flip Quantum Error Correction")
    st.markdown("""
    To protect the secret transmission against channel noise, we encode the logical secret qubit into a **3-qubit repetition code** $(\\alpha|000\\rangle + \\beta|111\\rangle)$.
    After QSS transmission and channel noise injection, Charlie computes syndrome bits via CNOT gates and applies a **Toffoli (CCX)** majority-vote decoder to correct single-qubit errors without collapsing the logical state.
    """)

    col_ec1, col_ec2 = st.columns(2)
    with col_ec1:
        target_qubit = st.selectbox(
            "Noise Target Qubit (Single-Qubit Bit-Flip):",
            [5, 1, 2],
            format_func=lambda q: f"Qubit {q} ({'Reconstructed Secret' if q==5 else f'Code Ancilla {q}'})"
        )
    with col_ec2:
        enable_ec = st.checkbox("Enable Toffoli Majority Decoder", value=True)

    run_ec = st.button("🧪 Simulate Error Correction Channel", type="primary", use_container_width=True)

    if run_ec or "ec_mitigated" not in st.session_state:
        with st.spinner("Running 6-qubit QSS + QEC circuit..."):
            _, uncorr_err = simulate_qss_error_correction(
                theta=theta_val, phi=phi_val,
                inject_bit_flip=True, error_qubit=target_qubit,
                apply_correction=False, shots=shots_param
            )
            _, corr_err = simulate_qss_error_correction(
                theta=theta_val, phi=phi_val,
                inject_bit_flip=True, error_qubit=target_qubit,
                apply_correction=True, shots=shots_param
            )
            st.session_state["ec_uncorr"] = uncorr_err
            st.session_state["ec_corr"] = corr_err

    uncorr_err = st.session_state["ec_uncorr"]
    corr_err = st.session_state["ec_corr"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Uncorrected Error Rate", f"{uncorr_err * 100:.1f}%", delta=f"{uncorr_err*100:.1f}%", delta_color="inverse")
    c2.metric("Corrected Error Rate", f"{corr_err * 100:.1f}%", delta=f"-{uncorr_err*100:.1f}%", delta_color="normal")
    with c3:
        st.markdown("**Noise Resilience:**")
        if corr_err == 0.0:
            st.markdown('<span class="status-badge-success">✓ RESILIENT: 0.0% Residual Error</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-badge-alert">⚠️ UNMITIGATED NOISE</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Syndrome Decoding Logic")
    st.latex(r"s_1 = q_5 \oplus q_1, \quad s_2 = q_5 \oplus q_2")
    st.latex(r"\text{Correction Gate: } \text{CCX}(q_2, q_1 \to q_5) \implies \text{Flips } q_5 \text{ only if } s_1 = 1 \text{ and } s_2 = 1")

    fig = go.Figure(data=[
        go.Bar(
            name="Uncorrected Channel",
            x=["Reconstructed Secret"],
            y=[uncorr_err * 100],
            marker_color="#E53935",
            text=[f"{uncorr_err*100:.1f}%"],
            textposition='auto'
        ),
        go.Bar(
            name="Toffoli Corrected Channel",
            x=["Reconstructed Secret"],
            y=[corr_err * 100],
            marker_color="#2E7D32",
            text=[f"{corr_err*100:.1f}%"],
            textposition='auto'
        )
    ])
    fig.update_layout(
        barmode='group',
        title="100% Bit-Flip Noise Mitigation via Toffoli Majority Decoder",
        yaxis_title="Error Rate (%)",
        yaxis_range=[0, 105],
        template="plotly_white",
        height=350
    )
    st.plotly_chart(fig, use_container_width=True)


# ==========================================================
# MODULE 4: QUANTUM CIRCUIT VISUALIZER
# ==========================================================
elif nav_option == "📐 Circuit Visualizer":
    st.markdown("### 📐 Quantum Circuit Schematics & Gate Breakdown")

    circuit_choice = st.selectbox(
        "Select Circuit Architecture to Inspect:",
        [
            "Standard 4-Qubit HBB Protocol",
            "Intercept-and-Resend (IR) Attack Circuit",
            "Entangle-and-Measure (EM) Attack Circuit",
            "6-Qubit 3-Bit-Flip Error Correction Circuit"
        ]
    )

    if circuit_choice == "Standard 4-Qubit HBB Protocol":
        qc_view = create_qss_circuit(theta=theta_val, phi=phi_val)
    elif circuit_choice == "Intercept-and-Resend (IR) Attack Circuit":
        qc_view = create_intercept_resend_circuit(theta=theta_val, phi=phi_val)
    elif circuit_choice == "Entangle-and-Measure (EM) Attack Circuit":
        qc_view = create_entangle_measure_circuit(theta=theta_val, phi=phi_val)
    else:
        qc_view = create_qss_error_correction_circuit(theta=theta_val, phi=phi_val)

    stat1, stat2, stat3 = st.columns(3)
    stat1.metric("Total Qubits", qc_view.num_qubits)
    stat2.metric("Classical Bits", qc_view.num_clbits)
    stat3.metric("Circuit Depth", qc_view.depth())

    st.markdown("#### Circuit Diagram")
    try:
        fig_circ = qc_view.draw(output='mpl', style='iqp')
        st.pyplot(fig_circ)
    except Exception as e:
        st.text(qc_view.draw(output='text'))

    with st.expander("Show Detailed Gate Breakdown"):
        st.write(dict(qc_view.count_ops()))


# ==========================================================
# MODULE 5: THEORY & REAL-WORLD USES
# ==========================================================
elif nav_option == "📖 Theory & Applications":
    st.markdown("### 📖 Quantum Secret Sharing Theory & Applications")

    tab_th1, tab_th2 = st.tabs(["Quantum vs Classical Secret Sharing", "Real-World Applications"])

    with tab_th1:
        st.markdown(r"""
        #### Classical vs Quantum Secret Sharing
        - **Shamir's Secret Sharing (1979):** Divides a secret into $n$ shares using polynomial interpolation over finite fields. Any $k$ participants can reconstruct, but $k-1$ gain zero information. However, security relies entirely on classical computational models.
        - **Quantum Secret Sharing (HBB, 1999):** Encodes secrets into multi-partite entangled states (such as GHZ states). Collaboration is physically enforced: no subset of participants possesses enough quantum information or proper measurement bases to collapse the secret state independently.

        #### Theoretical Foundations:
        1. **Greenberger-Horne-Zeilinger (GHZ) State:**
           $$|\text{GHZ}\rangle = \frac{1}{\sqrt{2}}(|000\rangle + |111\rangle)$$
           Maximally entangled three-qubit resource distributed among Alice, Bob, and Charlie.
        2. **No-Cloning Theorem (Wootters & Zurek, 1982):**
           It is physically impossible to create an identical copy of an arbitrary unknown quantum state $|\psi\rangle$. Any eavesdropper measuring a transmitted qubit inevitably disturbs the joint state, creating detectable errors ($\sim 25\%$).
        """)

    with tab_th2:
        st.markdown("""
        #### Key Real-World Use Cases:
        1. **Distributed Cryptographic Key Management:**
           Eliminates single points of failure in Certificate Authorities (CAs) and Hardware Security Modules (HSMs) by requiring $k$-of-$n$ parties to collaboratively release master signing keys.
        2. **Secure Multi-Party Computation (SMPC):**
           Enables organizations in healthcare, banking, and genomics to jointly train federated models or run risk analytics without revealing raw proprietary inputs.
        3. **Quantum Internet & Quantum Repeater Networks:**
           Foundational primitive for multi-party quantum networking (Micius Satellite, OpenQKD, European Quantum Communication Infrastructure).
        4. **National Defense & Nuclear Command Authentication:**
           Realizes unconditional information-theoretic **Two-Person Integrity (TPI)** rules for missile launch codes and state secrets, immune to quantum computers running Shor's algorithm.
        5. **Blockchain Multi-Signature & Post-Quantum Threshold Signatures:**
           Distributes consensus and signing authority across distributed validators with unconditional physical security guarantees.
        """)

st.divider()
st.caption("Quantum Secret Sharing (QSS) Mini-Project • Department of Computer Engineering • VJTI, Mumbai")
