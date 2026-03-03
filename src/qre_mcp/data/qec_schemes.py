"""Static reference data for supported Quantum Error Correction (QEC) schemes."""

from __future__ import annotations

QEC_SCHEMES: dict[str, dict] = {
    "surface_code": {
        "id": "surface_code",
        "name": "Surface Code",
        "description": (
            "The most widely studied topological quantum error correcting code. "
            "Requires only nearest-neighbor interactions, making it compatible with "
            "all gate-based qubit architectures. High threshold (~1%) and good "
            "scalability. Works with all 6 predefined qubit models."
        ),
        "compatible_instruction_sets": ["GateBased", "Majorana"],
        "threshold": "~1%",
        "distance_formula": "Odd code distances d ≥ 3",
        "physical_qubits_per_logical": "~2d²",
        "logical_cycle_time_description": (
            "Proportional to the code distance times the two-qubit gate time"
        ),
    },
    "floquet_code": {
        "id": "floquet_code",
        "name": "Floquet Code (Honeycomb Code)",
        "description": (
            "A periodic measurement-based quantum error correcting code optimized for "
            "Majorana-based topological qubits. Offers better physical qubit overhead "
            "than surface code for Majorana hardware due to the native measurement "
            "operations available. Compatible ONLY with Majorana qubit models "
            "(qubit_maj_ns_e4 and qubit_maj_ns_e6)."
        ),
        "compatible_instruction_sets": ["Majorana"],
        "threshold": "~1% (similar to surface code)",
        "distance_formula": "Even code distances d ≥ 2",
        "physical_qubits_per_logical": "~4d² / 3 (better than surface code for Majorana)",
        "logical_cycle_time_description": (
            "Proportional to the code distance times the measurement time"
        ),
        "note": (
            "Using floquet_code with gate-based qubit models will raise an error. "
            "Select qubit_maj_ns_e4 or qubit_maj_ns_e6 when using floquet_code."
        ),
    },
}

VALID_QEC_SCHEME_IDS = set(QEC_SCHEMES.keys())
MAJORANA_ONLY_SCHEMES = {"floquet_code"}
