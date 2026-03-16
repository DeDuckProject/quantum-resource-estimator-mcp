"""Guidance tools: explain_parameters and custom_qubit_model estimation."""

from __future__ import annotations

from typing import Any

from qre_mcp.core.estimator import run_estimation
from qre_mcp.core.params import build_params_dict
from qre_mcp.core.result_formatter import format_single_result
from qre_mcp.core.validators import (
    validate_algorithm_input,
    validate_error_budget,
    validate_logical_counts,
    validate_qec_scheme_params,
    validate_reaction_time,
)
from qre_mcp.data.algorithm_templates import ALGORITHM_TEMPLATES
from qre_mcp.data.qec_schemes import QEC_SCHEMES
from qre_mcp.data.qubit_models import QUBIT_MODELS


_USE_CASE_GUIDANCE: dict[str, dict] = {
    "cryptography": {
        "summary": (
            "Quantum attacks on classical cryptography (RSA, ECC, AES) use Shor's and "
            "Grover's algorithms. These require millions of physical qubits and years of "
            "runtime on current technology projections."
        ),
        "recommended_qubit_models": ["qubit_gate_ns_e3", "qubit_gate_ns_e4"],
        "recommended_qec_scheme": "surface_code",
        "recommended_error_budget": 0.001,
        "relevant_templates": ["shor_2048", "grover_aes128"],
        "key_parameters": {
            "qubit_model": "Use ns gate-based models (superconducting) for typical projections.",
            "error_budget": "0.001 is standard. Lower values give more conservative estimates.",
            "max_physical_qubits": "Set this to understand minimum hardware scale required.",
            "reaction_time": (
                "Classical control system latency. Use reaction_time='10 us' to model "
                "the Gidney-Ekeraa assumption where the classical reaction time (~10 µs) "
                "dominates the logical cycle time (~1 µs)."
            ),
        },
        "typical_results": (
            "Breaking RSA-2048 with Shor's algorithm requires on the order of millions "
            "of physical qubits and many hours to days of runtime — well beyond current capability."
        ),
    },
    "chemistry": {
        "summary": (
            "Quantum chemistry simulation uses quantum phase estimation (QPE) or VQE to "
            "find ground state energies of molecules. Key applications: drug discovery, "
            "catalyst design, battery materials."
        ),
        "recommended_qubit_models": ["qubit_gate_ns_e3", "qubit_gate_us_e3"],
        "recommended_qec_scheme": "surface_code",
        "recommended_error_budget": 0.01,
        "relevant_templates": ["chemistry_femo", "qpe_generic"],
        "key_parameters": {
            "error_budget": (
                "0.01 (1%) is often acceptable for chemistry; higher than crypto applications "
                "because chemical accuracy (~1 mHartree) tolerates some error."
            ),
            "qubit_model": (
                "Both fast (ns) and slow (μs) models are studied. Trapped-ion may have "
                "better error rates but slower clock speed."
            ),
            "logical_counts": (
                "For custom molecules, estimate numQubits from active space orbitals "
                "and T-count from the Hamiltonian simulation method."
            ),
        },
        "typical_results": (
            "FeMo-cofactor (54 orbitals) requires ~1 million physical qubits. "
            "Simpler molecules (20-30 orbitals) need ~100k-500k qubits."
        ),
    },
    "optimization": {
        "summary": (
            "Quantum optimization algorithms (QAOA, quantum annealing, Grover search) "
            "target combinatorial and continuous optimization problems. Quantum advantage "
            "is less clear-cut than chemistry or cryptography."
        ),
        "recommended_qubit_models": ["qubit_gate_ns_e3"],
        "recommended_qec_scheme": "surface_code",
        "recommended_error_budget": 0.001,
        "relevant_templates": ["qpe_generic"],
        "key_parameters": {
            "logical_counts": (
                "Provide custom logical_counts based on your specific problem size and QAOA depth."
            ),
            "error_budget": "0.001 is a good starting point.",
        },
        "typical_results": (
            "Resource requirements depend heavily on problem size and algorithm depth. "
            "Use logical_counts to provide your own circuit estimates."
        ),
    },
    "general": {
        "summary": (
            "For general quantum algorithm resource estimation, start with default parameters "
            "and iterate. The most important choices are qubit model (hardware technology) "
            "and error budget (acceptable failure probability)."
        ),
        "recommended_qubit_models": ["qubit_gate_ns_e3"],
        "recommended_qec_scheme": "surface_code",
        "recommended_error_budget": 0.001,
        "relevant_templates": list(ALGORITHM_TEMPLATES.keys()),
        "key_parameters": {
            "qubit_model": "Start with qubit_gate_ns_e3 (realistic superconducting).",
            "qec_scheme": "surface_code works for all qubit models.",
            "error_budget": (
                "0.001 means 1-in-1000 chance of failure. Lower = more physical qubits needed."
            ),
            "max_duration / max_physical_qubits": (
                "Use these constraints to find minimum hardware requirements under a time budget "
                "or qubit budget. They are mutually exclusive — use one or the other."
            ),
            "logical_depth_factor": (
                "Multiplier on logical circuit depth (default 1.0). Increase to model "
                "routing overhead or other compilation inefficiencies."
            ),
        },
        "workflow": (
            "1. Call list_algorithm_templates() to find a template or provide logical_counts.\n"
            "2. Call estimate_resources() with defaults to get a baseline.\n"
            "3. Call compare_configurations() to see how different hardware compares.\n"
            "4. Call generate_frontier() to see the qubit/time tradeoff.\n"
            "5. Use constraints (max_duration, max_physical_qubits) to explore feasibility."
        ),
    },
}


def explain_parameters(use_case: str | None = None) -> dict[str, Any]:
    """Explain resource estimation parameters and recommend starting configurations.

    If use_case is provided, gives targeted guidance for that domain.
    Valid use cases: 'cryptography', 'chemistry', 'optimization', 'general'.
    If omitted, returns a full parameter reference guide.
    """
    if use_case is not None:
        normalized = use_case.lower().strip()
        guidance = _USE_CASE_GUIDANCE.get(normalized, _USE_CASE_GUIDANCE["general"])
        return {
            "use_case": use_case,
            "guidance": guidance,
            "parameter_reference": _parameter_reference(),
            "qubit_model_options": list(QUBIT_MODELS.keys()),
            "qec_scheme_options": list(QEC_SCHEMES.keys()),
        }

    return {
        "parameter_reference": _parameter_reference(),
        "available_use_cases": list(_USE_CASE_GUIDANCE.keys()),
        "qubit_model_options": list(QUBIT_MODELS.keys()),
        "qec_scheme_options": list(QEC_SCHEMES.keys()),
        "tip": "Pass a use_case for targeted guidance: 'cryptography', 'chemistry', 'optimization'.",
    }


def custom_qubit_model_estimate(
    qsharp_code: str | None = None,
    algorithm_template: str | None = None,
    logical_counts: dict | None = None,
    # Custom qubit parameters
    instruction_set: str = "GateBased",
    one_qubit_gate_time: str = "50 ns",
    two_qubit_gate_time: str = "50 ns",
    one_qubit_measurement_time: str = "100 ns",
    one_qubit_gate_error_rate: float = 1e-3,
    two_qubit_gate_error_rate: float = 1e-3,
    t_gate_error_rate: float = 5e-4,
    readout_error_rate: float = 1e-3,
    idle_error_rate: float = 1e-4,
    qec_scheme: str = "surface_code",
    error_budget: float = 0.001,
    qec_crossing_prefactor: float | None = None,
    qec_error_correction_threshold: float | None = None,
    qec_logical_cycle_time: str | None = None,
    qec_physical_qubits_per_logical: str | None = None,
    reaction_time: str | None = None,
) -> dict[str, Any]:
    """Estimate resources using fully custom physical qubit parameters.

    Use this when modeling novel hardware that doesn't match any of the 6 predefined
    qubit models. All gate times accept strings like '50 ns', '1 μs', '100 ms'.
    instruction_set must be 'GateBased' or 'Majorana'.

    Optional reaction_time (e.g. '10 us') models classical control system latency.
    """
    validate_algorithm_input(qsharp_code, algorithm_template, logical_counts)
    validate_error_budget(error_budget)
    if logical_counts is not None:
        validate_logical_counts(logical_counts)
    validate_qec_scheme_params(
        qec_crossing_prefactor, qec_error_correction_threshold,
        qec_logical_cycle_time, qec_physical_qubits_per_logical,
    )

    reaction_time_ns: float | None = None
    if reaction_time is not None:
        reaction_time_ns = validate_reaction_time(reaction_time)

    custom_qubit_params = {
        "instructionSet": instruction_set,
        "oneQubitGateTime": one_qubit_gate_time,
        "twoQubitGateTime": two_qubit_gate_time,
        "oneQubitMeasurementTime": one_qubit_measurement_time,
        "oneQubitGateErrorRate": one_qubit_gate_error_rate,
        "twoQubitGateErrorRate": two_qubit_gate_error_rate,
        "tGateErrorRate": t_gate_error_rate,
        "readoutErrorRate": readout_error_rate,
        "idleErrorRate": idle_error_rate,
    }

    qec_params: dict[str, Any] = {"name": qec_scheme}
    if qec_crossing_prefactor is not None:
        qec_params["crossingPrefactor"] = qec_crossing_prefactor
    if qec_error_correction_threshold is not None:
        qec_params["errorCorrectionThreshold"] = qec_error_correction_threshold
    if qec_logical_cycle_time is not None:
        qec_params["logicalCycleTime"] = qec_logical_cycle_time
    if qec_physical_qubits_per_logical is not None:
        qec_params["physicalQubitsPerLogicalQubit"] = qec_physical_qubits_per_logical

    params: dict[str, Any] = {
        "qubitParams": custom_qubit_params,
        "qecScheme": qec_params,
        "errorBudget": error_budget,
    }

    raw = run_estimation(qsharp_code, algorithm_template, logical_counts, params)
    return format_single_result(raw, reaction_time_ns=reaction_time_ns)


def _parameter_reference() -> dict[str, Any]:
    return {
        "algorithm_input": {
            "qsharp_code": "Q# source code string. Must contain a parameterless entry point operation.",
            "algorithm_template": f"ID of a predefined template. Options: {list(ALGORITHM_TEMPLATES.keys())}",
            "logical_counts": (
                "Dict with keys: numQubits (required), tCount, cczCount, ccixCount, "
                "rotationCount, rotationDepth, measurementCount (all optional, default 0)."
            ),
        },
        "hardware": {
            "qubit_model": (
                f"Physical qubit model. Options: {list(QUBIT_MODELS.keys())}. "
                "Default: qubit_gate_ns_e3 (realistic superconducting)."
            ),
            "qec_scheme": (
                f"Quantum error correction scheme. Options: {list(QEC_SCHEMES.keys())}. "
                "floquet_code requires Majorana qubits. Default: surface_code."
            ),
            "error_budget": (
                "Acceptable probability of algorithm failure (0 to 1, exclusive). "
                "Default: 0.001. Lower = safer but requires more physical qubits."
            ),
        },
        "constraints": {
            "max_duration": (
                "Maximum allowed runtime (e.g. '1 s', '500 ms', '1 hour'). "
                "Mutually exclusive with max_physical_qubits."
            ),
            "max_physical_qubits": (
                "Maximum allowed physical qubit count (integer). "
                "Mutually exclusive with max_duration."
            ),
            "max_t_factories": (
                "Maximum number of T-factory copies to use. "
                "Reduces qubit count at the cost of longer runtime."
            ),
            "logical_depth_factor": (
                "Multiplier on logical circuit depth (default 1.0). "
                "Increase to model routing overhead or compilation inefficiency."
            ),
        },
        "error_budget_breakdown": {
            "error_budget_logical": "Budget for logical errors (default: 1/3 of total).",
            "error_budget_t_states": "Budget for T-state distillation errors (default: 1/3 of total).",
            "error_budget_rotations": "Budget for rotation synthesis errors (default: 1/3 of total).",
        },
        "qubit_model_overrides": (
            "JSON string. Start from a named qubit_model and override specific parameters. "
            "E.g. '{\"twoQubitGateTime\": \"10 ns\"}' to keep qubit_gate_ns_e3 but change gate time. "
            "Valid keys: oneQubitGateTime, twoQubitGateTime, oneQubitMeasurementTime, "
            "oneQubitGateErrorRate, twoQubitGateErrorRate, tGateErrorRate, readoutErrorRate, idleErrorRate."
        ),
        "reaction_time": (
            "Classical control system reaction time, e.g. '10 us'. When the reaction time "
            "exceeds the QEC logical cycle time, it becomes the effective cycle time, "
            "increasing overall runtime. This models the Gidney-Ekeraa scenario where "
            "classical decoding latency (~10 µs) dominates the logical cycle (~1 µs). "
            "Only affects runtime — physical qubit count and code distance are unchanged."
        ),
        "custom_qec_scheme": {
            "qec_crossing_prefactor": (
                "float > 0. Overrides the error-suppression prefactor "
                "(default ~0.03 for surface code)."
            ),
            "qec_error_correction_threshold": (
                "float in (0,1). Overrides the error correction threshold (default ~0.01)."
            ),
            "qec_logical_cycle_time": (
                "Formula string for one logical cycle duration. Variables: twoQubitGateTime, "
                "oneQubitMeasurementTime, codeDistance. "
                "E.g. '(4 * twoQubitGateTime + 2 * oneQubitMeasurementTime) * codeDistance'. "
                "Use '1000 ns' (a constant) to fix cycle time to 1 µs regardless of code distance."
            ),
            "qec_physical_qubits_per_logical": (
                "Formula string for physical qubits per logical qubit. Variable: codeDistance. "
                "E.g. '2 * codeDistance * codeDistance' (surface code default)."
            ),
        },
    }
