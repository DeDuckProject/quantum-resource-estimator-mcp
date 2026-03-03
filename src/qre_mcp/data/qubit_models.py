"""Static reference data for the 6 predefined physical qubit models."""

from __future__ import annotations

QUBIT_MODELS: dict[str, dict] = {
    "qubit_gate_ns_e3": {
        "id": "qubit_gate_ns_e3",
        "name": "Gate-based (ns, 10⁻³)",
        "technology": "Superconducting / Spin qubit",
        "instruction_set": "GateBased",
        "description": (
            "Fast gate-based qubit with nanosecond gate times and 10⁻³ error rate. "
            "Representative of near-term superconducting or spin qubit devices. "
            "Optimistic but achievable error rates for current hardware."
        ),
        "one_qubit_gate_time": "50 ns",
        "two_qubit_gate_time": "50 ns",
        "one_qubit_measurement_time": "100 ns",
        "one_qubit_gate_error_rate": 1e-3,
        "two_qubit_gate_error_rate": 1e-3,
        "t_gate_error_rate": 5e-4,
        "readout_error_rate": 1e-3,
        "idle_error_rate": 1e-4,
    },
    "qubit_gate_ns_e4": {
        "id": "qubit_gate_ns_e4",
        "name": "Gate-based (ns, 10⁻⁴)",
        "technology": "Superconducting / Spin qubit (improved)",
        "instruction_set": "GateBased",
        "description": (
            "Fast gate-based qubit with nanosecond gate times and 10⁻⁴ error rate. "
            "Represents an optimistic future superconducting or spin qubit with "
            "significantly improved error rates. Good for projections."
        ),
        "one_qubit_gate_time": "50 ns",
        "two_qubit_gate_time": "50 ns",
        "one_qubit_measurement_time": "100 ns",
        "one_qubit_gate_error_rate": 1e-4,
        "two_qubit_gate_error_rate": 1e-4,
        "t_gate_error_rate": 5e-5,
        "readout_error_rate": 1e-4,
        "idle_error_rate": 1e-5,
    },
    "qubit_gate_us_e3": {
        "id": "qubit_gate_us_e3",
        "name": "Gate-based (μs, 10⁻³)",
        "technology": "Trapped-ion qubit",
        "instruction_set": "GateBased",
        "description": (
            "Slower gate-based qubit with microsecond gate times and 10⁻³ error rate. "
            "Representative of current trapped-ion devices (e.g., IonQ, Quantinuum). "
            "Higher fidelity potential but slower clock speed than superconducting."
        ),
        "one_qubit_gate_time": "100 μs",
        "two_qubit_gate_time": "100 μs",
        "one_qubit_measurement_time": "100 μs",
        "one_qubit_gate_error_rate": 1e-3,
        "two_qubit_gate_error_rate": 1e-3,
        "t_gate_error_rate": 5e-4,
        "readout_error_rate": 1e-3,
        "idle_error_rate": 1e-4,
    },
    "qubit_gate_us_e4": {
        "id": "qubit_gate_us_e4",
        "name": "Gate-based (μs, 10⁻⁴)",
        "technology": "Trapped-ion qubit (improved)",
        "instruction_set": "GateBased",
        "description": (
            "Slower gate-based qubit with microsecond gate times and 10⁻⁴ error rate. "
            "Represents optimistic future trapped-ion performance. Very high fidelity "
            "but slow gate times means long runtimes for large circuits."
        ),
        "one_qubit_gate_time": "100 μs",
        "two_qubit_gate_time": "100 μs",
        "one_qubit_measurement_time": "100 μs",
        "one_qubit_gate_error_rate": 1e-4,
        "two_qubit_gate_error_rate": 1e-4,
        "t_gate_error_rate": 5e-5,
        "readout_error_rate": 1e-4,
        "idle_error_rate": 1e-5,
    },
    "qubit_maj_ns_e4": {
        "id": "qubit_maj_ns_e4",
        "name": "Majorana (ns, 10⁻⁴)",
        "technology": "Topological / Majorana qubit",
        "instruction_set": "Majorana",
        "description": (
            "Topological qubit based on Majorana zero modes with nanosecond operation "
            "times and 10⁻⁴ error rate. Intrinsic topological protection provides "
            "better qubit overhead. Compatible with floquet_code QEC only. "
            "Representative of Microsoft's topological qubit approach."
        ),
        "one_qubit_gate_time": "100 ns",
        "two_qubit_gate_time": "100 ns",
        "one_qubit_measurement_time": "100 ns",
        "one_qubit_gate_error_rate": 1e-4,
        "two_qubit_gate_error_rate": 1e-4,
        "t_gate_error_rate": 5e-5,
        "readout_error_rate": 1e-4,
        "idle_error_rate": 1e-6,
    },
    "qubit_maj_ns_e6": {
        "id": "qubit_maj_ns_e6",
        "name": "Majorana (ns, 10⁻⁶)",
        "technology": "Topological / Majorana qubit (optimistic)",
        "instruction_set": "Majorana",
        "description": (
            "Highly optimistic topological qubit with nanosecond operation times and "
            "10⁻⁶ error rate. Represents the long-term potential of topological "
            "qubits with dramatically reduced overhead. Compatible with floquet_code "
            "QEC only. Use for long-term projections."
        ),
        "one_qubit_gate_time": "100 ns",
        "two_qubit_gate_time": "100 ns",
        "one_qubit_measurement_time": "100 ns",
        "one_qubit_gate_error_rate": 1e-6,
        "two_qubit_gate_error_rate": 1e-6,
        "t_gate_error_rate": 5e-7,
        "readout_error_rate": 1e-6,
        "idle_error_rate": 1e-8,
    },
}

VALID_QUBIT_MODEL_IDS = set(QUBIT_MODELS.keys())
MAJORANA_QUBIT_MODEL_IDS = {"qubit_maj_ns_e4", "qubit_maj_ns_e6"}
GATE_BASED_QUBIT_MODEL_IDS = VALID_QUBIT_MODEL_IDS - MAJORANA_QUBIT_MODEL_IDS
