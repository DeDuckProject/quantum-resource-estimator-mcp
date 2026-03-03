"""Input validation and compatibility checks for resource estimation parameters."""

from __future__ import annotations

from qre_mcp.data.qec_schemes import MAJORANA_ONLY_SCHEMES, VALID_QEC_SCHEME_IDS
from qre_mcp.data.qubit_models import (
    GATE_BASED_QUBIT_MODEL_IDS,
    VALID_QUBIT_MODEL_IDS,
)
from qre_mcp.errors import (
    AlgorithmInputError,
    IncompatibleQECSchemeError,
    InvalidErrorBudgetError,
    InvalidQubitModelError,
)


def validate_qubit_model(model: str) -> None:
    if model not in VALID_QUBIT_MODEL_IDS:
        valid = ", ".join(sorted(VALID_QUBIT_MODEL_IDS))
        raise InvalidQubitModelError(
            f"Unknown qubit model '{model}'. Valid options: {valid}. "
            "Use list_qubit_models() to see descriptions of each model."
        )


def validate_qec_scheme(scheme: str) -> None:
    if scheme not in VALID_QEC_SCHEME_IDS:
        valid = ", ".join(sorted(VALID_QEC_SCHEME_IDS))
        raise InvalidQubitModelError(
            f"Unknown QEC scheme '{scheme}'. Valid options: {valid}. "
            "Use list_qec_schemes() to see descriptions of each scheme."
        )


def validate_qubit_model_qec_compatibility(model: str, scheme: str) -> None:
    if scheme in MAJORANA_ONLY_SCHEMES and model in GATE_BASED_QUBIT_MODEL_IDS:
        raise IncompatibleQECSchemeError(
            f"QEC scheme '{scheme}' is only compatible with Majorana qubit models "
            f"(qubit_maj_ns_e4, qubit_maj_ns_e6), but '{model}' is a gate-based qubit. "
            "Either switch to a Majorana qubit model or use 'surface_code' instead."
        )


def validate_error_budget(
    error_budget: float,
    logical: float | None = None,
    t_states: float | None = None,
    rotations: float | None = None,
) -> None:
    if not (0.0 < error_budget < 1.0):
        raise InvalidErrorBudgetError(
            f"error_budget must be between 0 and 1 (exclusive), got {error_budget}. "
            "Typical values: 0.001 (1 in 1000), 0.01 (1 in 100)."
        )
    components = [v for v in (logical, t_states, rotations) if v is not None]
    if components:
        total = sum(components)
        if not (0.0 < total < 1.0):
            raise InvalidErrorBudgetError(
                f"The sum of error budget components must be between 0 and 1 "
                f"(exclusive), got {total:.4f} ({logical=}, {t_states=}, {rotations=})."
            )


def validate_algorithm_input(
    qsharp_code: str | None,
    algorithm_template: str | None,
    logical_counts: dict | None,
) -> None:
    provided = sum(v is not None for v in (qsharp_code, algorithm_template, logical_counts))
    if provided == 0:
        raise AlgorithmInputError(
            "No algorithm input provided. Supply exactly one of: "
            "'qsharp_code' (Q# source), 'algorithm_template' (e.g. 'shor_2048'), "
            "or 'logical_counts' (dict with numQubits, tCount, etc.)."
        )
    if provided > 1:
        raise AlgorithmInputError(
            "Multiple algorithm inputs provided. Supply exactly one of: "
            "'qsharp_code', 'algorithm_template', or 'logical_counts'."
        )


def validate_logical_counts(counts: dict) -> None:
    if "numQubits" not in counts:
        raise AlgorithmInputError(
            "logical_counts must include 'numQubits'. "
            "Also provide at least one of: 'tCount', 'cczCount', 'rotationCount'."
        )
    if counts.get("numQubits", 0) <= 0:
        raise AlgorithmInputError("logical_counts['numQubits'] must be a positive integer.")
