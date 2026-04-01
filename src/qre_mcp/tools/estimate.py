"""Primary estimation tools: estimate_resources and generate_frontier."""

from __future__ import annotations

from typing import Any

from qre_mcp.core.estimator import run_estimation, run_frontier_estimation
from qre_mcp.core.params import build_params_dict
from qre_mcp.core.result_formatter import format_frontier_results, format_single_result
from qre_mcp.data.algorithm_templates import ALGORITHM_TEMPLATES
from qre_mcp.core.validators import (
    validate_algorithm_input,
    validate_error_budget,
    validate_logical_counts,
    validate_qec_scheme,
    validate_qec_scheme_params,
    validate_qubit_model,
    validate_qubit_model_overrides,
    validate_qubit_model_qec_compatibility,
)


def estimate_resources(
    qsharp_code: str | None = None,
    algorithm_template: str | None = None,
    logical_counts: dict | None = None,
    qubit_model: str = "qubit_gate_ns_e3",
    qec_scheme: str = "surface_code",
    error_budget: float = 0.001,
    max_duration: str | None = None,
    max_physical_qubits: int | None = None,
    max_t_factories: int | None = None,
    logical_depth_factor: float | None = None,
    error_budget_logical: float | None = None,
    error_budget_t_states: float | None = None,
    error_budget_rotations: float | None = None,
    qubit_model_overrides: dict | None = None,
    qec_crossing_prefactor: float | None = None,
    qec_error_correction_threshold: float | None = None,
    qec_logical_cycle_time: str | None = None,
    qec_physical_qubits_per_logical: str | None = None,
) -> dict[str, Any]:
    """Estimate the physical quantum resources required to run a quantum algorithm.

    Provide the algorithm as exactly one of:
    - qsharp_code: Q# source code string with a parameterless entry point operation
    - algorithm_template: ID of a predefined template (e.g. 'shor_2048', 'grover_aes128')
    - logical_counts: dict with keys numQubits, tCount, rotationCount, cczCount, etc.

    Returns a summary (physical qubits, runtime, logical qubits, code distance, T factories)
    plus a full details breakdown.
    """
    validate_algorithm_input(qsharp_code, algorithm_template, logical_counts)
    validate_qubit_model(qubit_model)
    validate_qec_scheme(qec_scheme)
    validate_qubit_model_qec_compatibility(qubit_model, qec_scheme)
    validate_error_budget(error_budget, error_budget_logical, error_budget_t_states, error_budget_rotations)
    if logical_counts is not None:
        validate_logical_counts(logical_counts)
    if qubit_model_overrides:
        validate_qubit_model_overrides(qubit_model_overrides)
    validate_qec_scheme_params(
        qec_crossing_prefactor, qec_error_correction_threshold,
        qec_logical_cycle_time, qec_physical_qubits_per_logical,
    )

    params = build_params_dict(
        qubit_model=qubit_model,
        qec_scheme=qec_scheme,
        error_budget=error_budget,
        max_duration=max_duration,
        max_physical_qubits=max_physical_qubits,
        max_t_factories=max_t_factories,
        logical_depth_factor=logical_depth_factor,
        error_budget_logical=error_budget_logical,
        error_budget_t_states=error_budget_t_states,
        error_budget_rotations=error_budget_rotations,
        qubit_model_overrides=qubit_model_overrides,
        qec_crossing_prefactor=qec_crossing_prefactor,
        qec_error_correction_threshold=qec_error_correction_threshold,
        qec_logical_cycle_time=qec_logical_cycle_time,
        qec_physical_qubits_per_logical=qec_physical_qubits_per_logical,
    )

    raw = run_estimation(qsharp_code, algorithm_template, logical_counts, params)

    template_info = None
    if algorithm_template is not None and algorithm_template in ALGORITHM_TEMPLATES:
        t = ALGORITHM_TEMPLATES[algorithm_template]
        template_info = {
            "name": t.name,
            "source": t.source,
            "caveats": list(t.caveats),
        }

    return format_single_result(raw, template_info=template_info)


def generate_frontier(
    qsharp_code: str | None = None,
    algorithm_template: str | None = None,
    logical_counts: dict | None = None,
    qubit_model: str = "qubit_gate_ns_e3",
    qec_scheme: str = "surface_code",
    error_budget: float = 0.001,
    qubit_model_overrides: dict | None = None,
    qec_crossing_prefactor: float | None = None,
    qec_error_correction_threshold: float | None = None,
    qec_logical_cycle_time: str | None = None,
    qec_physical_qubits_per_logical: str | None = None,
) -> dict[str, Any]:
    """Generate the Pareto frontier showing the qubit-count vs. runtime tradeoff.

    Each point on the frontier is optimal: reducing qubits increases runtime and vice versa.
    The first point minimizes qubit count; the last minimizes runtime.

    Provide the algorithm as exactly one of qsharp_code, algorithm_template, or logical_counts.
    """
    validate_algorithm_input(qsharp_code, algorithm_template, logical_counts)
    validate_qubit_model(qubit_model)
    validate_qec_scheme(qec_scheme)
    validate_qubit_model_qec_compatibility(qubit_model, qec_scheme)
    validate_error_budget(error_budget)
    if logical_counts is not None:
        validate_logical_counts(logical_counts)
    if qubit_model_overrides:
        validate_qubit_model_overrides(qubit_model_overrides)
    validate_qec_scheme_params(
        qec_crossing_prefactor, qec_error_correction_threshold,
        qec_logical_cycle_time, qec_physical_qubits_per_logical,
    )

    params = build_params_dict(
        qubit_model=qubit_model,
        qec_scheme=qec_scheme,
        error_budget=error_budget,
        qubit_model_overrides=qubit_model_overrides,
        qec_crossing_prefactor=qec_crossing_prefactor,
        qec_error_correction_threshold=qec_error_correction_threshold,
        qec_logical_cycle_time=qec_logical_cycle_time,
        qec_physical_qubits_per_logical=qec_physical_qubits_per_logical,
    )

    raw = run_frontier_estimation(qsharp_code, algorithm_template, logical_counts, params)
    return format_frontier_results(raw)
