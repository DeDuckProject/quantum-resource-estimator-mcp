"""Comparison tools: compare_configurations across hardware architectures."""

from __future__ import annotations

from typing import Any

from qre_mcp.core.estimator import run_batch_estimation
from qre_mcp.core.params import all_qubit_model_configs, build_params_list
from qre_mcp.core.result_formatter import format_batch_results
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


def compare_configurations(
    qsharp_code: str | None = None,
    algorithm_template: str | None = None,
    logical_counts: dict | None = None,
    qubit_models: list[str] | None = None,
    compare_all_models: bool = False,
    qec_scheme: str = "surface_code",
    error_budget: float = 0.001,
    configurations: list[dict] | None = None,
) -> dict[str, Any]:
    """Compare resource estimates across multiple hardware configurations.

    Provide the algorithm as exactly one of qsharp_code, algorithm_template, or logical_counts.

    Specify hardware configurations in one of three ways (mutually exclusive):
    - compare_all_models=True: compare all 6 qubit models (or Majorana-only if floquet_code)
    - qubit_models=['qubit_gate_ns_e3', 'qubit_gate_us_e3', ...]: compare specific models
    - configurations=[{'qubit_model': ..., 'qec_scheme': ..., 'error_budget': ...}, ...]:
      full custom configurations including different QEC schemes and error budgets

    Returns a side-by-side comparison table.
    """
    validate_algorithm_input(qsharp_code, algorithm_template, logical_counts)
    validate_error_budget(error_budget)
    if logical_counts is not None:
        validate_logical_counts(logical_counts)

    # Build the list of parameter configs to run
    if configurations is not None:
        for cfg in configurations:
            validate_qubit_model(cfg.get("qubit_model", "qubit_gate_ns_e3"))
            validate_qec_scheme(cfg.get("qec_scheme", "surface_code"))
            validate_qubit_model_qec_compatibility(
                cfg.get("qubit_model", "qubit_gate_ns_e3"),
                cfg.get("qec_scheme", "surface_code"),
            )
            if cfg.get("qubit_model_overrides"):
                validate_qubit_model_overrides(cfg["qubit_model_overrides"])
            validate_qec_scheme_params(
                cfg.get("qec_crossing_prefactor"),
                cfg.get("qec_error_correction_threshold"),
                cfg.get("qec_logical_cycle_time"),
                cfg.get("qec_physical_qubits_per_logical"),
            )
        params_list = build_params_list(configurations)
        config_labels = configurations

    elif compare_all_models:
        validate_qec_scheme(qec_scheme)
        configs = all_qubit_model_configs(qec_scheme=qec_scheme, error_budget=error_budget)
        params_list = build_params_list(configs)
        config_labels = configs

    elif qubit_models is not None:
        validate_qec_scheme(qec_scheme)
        configs = []
        for model in qubit_models:
            validate_qubit_model(model)
            validate_qubit_model_qec_compatibility(model, qec_scheme)
            configs.append({"qubit_model": model, "qec_scheme": qec_scheme, "error_budget": error_budget})
        params_list = build_params_list(configs)
        config_labels = configs

    else:
        # Default: compare all 4 gate-based models with surface_code
        from qre_mcp.data.qubit_models import GATE_BASED_QUBIT_MODEL_IDS
        configs = [
            {"qubit_model": m, "qec_scheme": "surface_code", "error_budget": error_budget}
            for m in sorted(GATE_BASED_QUBIT_MODEL_IDS)
        ]
        params_list = build_params_list(configs)
        config_labels = configs

    raw_results = run_batch_estimation(qsharp_code, algorithm_template, logical_counts, params_list)
    return format_batch_results(raw_results, config_labels)
