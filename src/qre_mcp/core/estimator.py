"""Single point of contact with the qsharp resource estimator.

All tools route estimation calls through this module.
"""

from __future__ import annotations

from typing import Any

from qre_mcp.data.algorithm_templates import ALGORITHM_TEMPLATES
from qre_mcp.errors import (
    AlgorithmInputError,
    EstimationFailedError,
    NoFeasibleSolutionError,
    UnknownAlgorithmTemplateError,
)


def run_estimation(
    qsharp_code: str | None,
    algorithm_template: str | None,
    logical_counts: dict | None,
    params: dict[str, Any],
) -> dict[str, Any]:
    """Run a single resource estimation.

    Exactly one of qsharp_code, algorithm_template, or logical_counts must be provided.
    params is a dict built by core.params.build_params_dict().
    """
    try:
        import qsharp
        from qsharp.estimator import EstimatorParams, LogicalCounts
    except ImportError as exc:
        raise EstimationFailedError(
            "The 'qsharp' package is not installed. "
            "Install it with: pip install qsharp"
        ) from exc

    try:
        if logical_counts is not None:
            lc = LogicalCounts(logical_counts)
            result = lc.estimate(EstimatorParams.from_dict(params))
            return result.as_dict()

        elif algorithm_template is not None:
            template = _get_template(algorithm_template)
            lc = LogicalCounts(template.logical_counts)
            result = lc.estimate(EstimatorParams.from_dict(params))
            return result.as_dict()

        elif qsharp_code is not None:
            result = qsharp.estimate(qsharp_code, params=params)
            return result.as_dict() if hasattr(result, "as_dict") else result

        else:
            raise AlgorithmInputError("No algorithm input provided.")

    except (AlgorithmInputError, UnknownAlgorithmTemplateError):
        raise
    except Exception as exc:
        _handle_qsharp_error(exc)


def run_batch_estimation(
    qsharp_code: str | None,
    algorithm_template: str | None,
    logical_counts: dict | None,
    params_list: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Run estimation for multiple parameter configurations."""
    results = []
    for params in params_list:
        result = run_estimation(qsharp_code, algorithm_template, logical_counts, params)
        results.append(result)
    return results


def run_frontier_estimation(
    qsharp_code: str | None,
    algorithm_template: str | None,
    logical_counts: dict | None,
    params: dict[str, Any],
) -> Any:
    """Run Pareto frontier (time vs qubits) estimation."""
    try:
        import qsharp
        from qsharp.estimator import EstimatorParams, LogicalCounts
    except ImportError as exc:
        raise EstimationFailedError(
            "The 'qsharp' package is not installed. "
            "Install it with: pip install qsharp"
        ) from exc

    # Set estimate type to frontier
    frontier_params = dict(params)
    frontier_params["estimateType"] = "frontier"

    try:
        if logical_counts is not None:
            lc = LogicalCounts(logical_counts)
            result = lc.estimate(EstimatorParams.from_dict(frontier_params))
            return result.as_dict() if hasattr(result, "as_dict") else result

        elif algorithm_template is not None:
            template = _get_template(algorithm_template)
            lc = LogicalCounts(template.logical_counts)
            result = lc.estimate(EstimatorParams.from_dict(frontier_params))
            return result.as_dict() if hasattr(result, "as_dict") else result

        elif qsharp_code is not None:
            result = qsharp.estimate(qsharp_code, params=frontier_params)
            return result.as_dict() if hasattr(result, "as_dict") else result

        else:
            raise AlgorithmInputError("No algorithm input provided.")

    except (AlgorithmInputError, UnknownAlgorithmTemplateError):
        raise
    except Exception as exc:
        _handle_qsharp_error(exc)


def _get_template(template_id: str):
    if template_id not in ALGORITHM_TEMPLATES:
        valid = ", ".join(sorted(ALGORITHM_TEMPLATES.keys()))
        raise UnknownAlgorithmTemplateError(
            f"Unknown algorithm template '{template_id}'. "
            f"Valid templates: {valid}. "
            "Use list_algorithm_templates() for descriptions."
        )
    return ALGORITHM_TEMPLATES[template_id]


def _handle_qsharp_error(exc: Exception) -> None:
    msg = str(exc)
    if "no feasible" in msg.lower() or "infeasible" in msg.lower():
        raise NoFeasibleSolutionError(
            f"No feasible solution found under the given constraints. "
            f"Try relaxing max_duration, max_physical_qubits, or max_t_factories. "
            f"Original error: {msg}"
        ) from exc
    raise EstimationFailedError(
        f"Resource estimation failed: {msg}. "
        "Check that your Q# code compiles and that parameters are valid."
    ) from exc
