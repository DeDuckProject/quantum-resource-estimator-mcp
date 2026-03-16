"""Builds qsharp EstimatorParams from tool inputs."""

from __future__ import annotations

import re
from typing import Any

# qsharp's logicalCycleTime formula field only accepts a dimensionless number
# (nanoseconds) or a symbolic expression — unit suffixes like "ns"/"us" are rejected.
_DURATION_UNITS_NS = {
    "ns": 1,
    "us": 1_000,
    "µs": 1_000,
    "ms": 1_000_000,
    "s":  1_000_000_000,
}
_DURATION_RE = re.compile(
    r"^\s*([0-9]*\.?[0-9]+(?:[eE][+-]?[0-9]+)?)\s*(" +
    "|".join(re.escape(u) for u in _DURATION_UNITS_NS) +
    r")\s*$"
)


def _parse_cycle_time(value: str) -> str:
    """Convert a human duration string to a nanosecond number string.

    Accepts "1000 ns", "1 us", "1 µs", "0.5 ms", "1e3 ns", etc.
    Returns the plain nanosecond string expected by qsharp (e.g. "1000").
    Passes through values that don't match (e.g. formula expressions).
    """
    m = _DURATION_RE.match(value)
    if m:
        amount, unit = float(m.group(1)), m.group(2)
        ns = amount * _DURATION_UNITS_NS[unit]
        # Return integer string if whole, float string otherwise
        return str(int(ns)) if ns == int(ns) else str(ns)
    return value  # formula expression — pass through unchanged


def parse_duration_ns(value: str) -> float:
    """Parse a human duration string and return the value in nanoseconds.

    Accepts "1000 ns", "10 us", "10 µs", "0.5 ms", "1e3 ns", etc.
    Raises ValueError if the format is not recognised.
    """
    m = _DURATION_RE.match(value)
    if not m:
        raise ValueError(
            f"Invalid duration format: '{value}'. "
            "Expected a number followed by a unit (ns, us, µs, ms, s). "
            "Examples: '10 us', '1000 ns', '0.5 ms'."
        )
    amount, unit = float(m.group(1)), m.group(2)
    return amount * _DURATION_UNITS_NS[unit]


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
    qubit_model_overrides: dict | None = None,
    qec_crossing_prefactor: float | None = None,
    qec_error_correction_threshold: float | None = None,
    qec_logical_cycle_time: str | None = None,
    qec_physical_qubits_per_logical: str | None = None,
) -> dict[str, Any]:
    """Build a parameters dict compatible with qsharp.estimate(params=...)."""
    qubit_params: dict[str, Any] = {"name": qubit_model}
    if qubit_model_overrides:
        qubit_params.update(qubit_model_overrides)

    qec_params: dict[str, Any] = {"name": qec_scheme}
    if qec_crossing_prefactor is not None:
        qec_params["crossingPrefactor"] = qec_crossing_prefactor
    if qec_error_correction_threshold is not None:
        qec_params["errorCorrectionThreshold"] = qec_error_correction_threshold
    if qec_logical_cycle_time is not None:
        qec_params["logicalCycleTime"] = _parse_cycle_time(qec_logical_cycle_time)
    if qec_physical_qubits_per_logical is not None:
        qec_params["physicalQubitsPerLogicalQubit"] = qec_physical_qubits_per_logical

    params: dict[str, Any] = {
        "qubitParams": qubit_params,
        "qecScheme": qec_params,
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
