"""Builds qsharp EstimatorParams from tool inputs."""

from __future__ import annotations

from typing import Any


def build_params_dict(
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
) -> dict[str, Any]:
    """Build a parameters dict compatible with qsharp.estimate(params=...)."""
    params: dict[str, Any] = {
        "qubitParams": {"name": qubit_model},
        "qecScheme": {"name": qec_scheme},
        "errorBudget": error_budget,
    }

    # Override error budget with per-component breakdown if provided
    if any(v is not None for v in (error_budget_logical, error_budget_t_states, error_budget_rotations)):
        budget: dict[str, float] = {}
        if error_budget_logical is not None:
            budget["logical"] = error_budget_logical
        if error_budget_t_states is not None:
            budget["tStates"] = error_budget_t_states
        if error_budget_rotations is not None:
            budget["rotations"] = error_budget_rotations
        params["errorBudget"] = budget

    constraints: dict[str, Any] = {}
    if max_duration is not None:
        constraints["maxDuration"] = max_duration
    if max_physical_qubits is not None:
        constraints["maxPhysicalQubits"] = max_physical_qubits
    if max_t_factories is not None:
        constraints["maxTFactories"] = max_t_factories
    if logical_depth_factor is not None:
        constraints["logicalDepthFactor"] = logical_depth_factor
    if constraints:
        params["constraints"] = constraints

    return params


def build_params_list(configurations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build a list of params dicts for batch/compare estimation."""
    return [build_params_dict(**cfg) for cfg in configurations]


def all_qubit_model_configs(
    qec_scheme: str = "surface_code",
    error_budget: float = 0.001,
) -> list[dict[str, Any]]:
    """Return one config per qubit model for comparison."""
    from qre_mcp.data.qubit_models import VALID_QUBIT_MODEL_IDS
    from qre_mcp.data.qec_schemes import MAJORANA_ONLY_SCHEMES
    from qre_mcp.data.qubit_models import GATE_BASED_QUBIT_MODEL_IDS

    configs = []
    for model_id in sorted(VALID_QUBIT_MODEL_IDS):
        # If floquet_code requested, skip gate-based qubits (incompatible)
        if qec_scheme in MAJORANA_ONLY_SCHEMES and model_id in GATE_BASED_QUBIT_MODEL_IDS:
            continue
        configs.append({"qubit_model": model_id, "qec_scheme": qec_scheme, "error_budget": error_budget})
    return configs
