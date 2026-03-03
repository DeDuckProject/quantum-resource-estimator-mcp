"""Single point of contact with the qsharp resource estimator.

All tools route estimation calls through this module.
"""

from __future__ import annotations

import json
import threading
import time
from typing import Any

from qre_mcp._log import logger
from qre_mcp.data.algorithm_templates import ALGORITHM_TEMPLATES
from qre_mcp.errors import (
    AlgorithmInputError,
    EstimationFailedError,
    NoFeasibleSolutionError,
    UnknownAlgorithmTemplateError,
)

# Maximum seconds to wait for a single qsharp estimation call.
# Combined QEC overrides + tight constraints can cause the estimator to search
# indefinitely; this cap ensures we fail fast with a useful error instead.
_ESTIMATION_TIMEOUT_S = 60


def _call_with_timeout(fn, timeout_s: int = _ESTIMATION_TIMEOUT_S):
    """Call fn() in a daemon thread; raise EstimationFailedError on timeout.

    fn must be a zero-argument callable (use a lambda to capture arguments).
    """
    result: list = [None]
    exc: list = [None]

    def _target():
        try:
            result[0] = fn()
        except Exception as e:  # noqa: BLE001
            exc[0] = e

    t = threading.Thread(target=_target, daemon=True)
    t.start()
    t.join(timeout=timeout_s)

    if t.is_alive():
        raise EstimationFailedError(
            f"Resource estimation timed out after {timeout_s}s. "
            "This commonly occurs when custom QEC parameters (e.g. logicalCycleTime) "
            "are combined with tight constraints (e.g. max_physical_qubits) that "
            "cannot be satisfied. Try removing constraints or using default QEC parameters."
        )

    if exc[0] is not None:
        raise exc[0]

    return result[0]


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
        from qsharp.estimator import LogicalCounts
    except ImportError as exc:
        raise EstimationFailedError(
            "The 'qsharp' package is not installed. "
            "Install it with: pip install qsharp"
        ) from exc

    logger.debug("run_estimation params: %s", json.dumps(params, default=str))
    t0 = time.monotonic()
    try:
        if logical_counts is not None:
            lc = LogicalCounts(logical_counts)
            logger.info(
                "run_estimation: calling LogicalCounts.estimate (logical_counts=%s)",
                json.dumps({k: v for k, v in logical_counts.items() if v}),
            )
            _log_params_debug_hints(params)
            result = _call_with_timeout(lambda: lc.estimate(params))
            raw = dict(result)

        elif algorithm_template is not None:
            template = _get_template(algorithm_template)
            lc = LogicalCounts(template.logical_counts)
            lc_summary = {k: v for k, v in template.logical_counts.items() if v}
            logger.info(
                "run_estimation: calling LogicalCounts.estimate (template=%r, logical_counts=%s)",
                algorithm_template, json.dumps(lc_summary),
            )
            _log_params_debug_hints(params)
            result = _call_with_timeout(lambda: lc.estimate(params))
            raw = dict(result)

        elif qsharp_code is not None:
            logger.info("run_estimation: calling qsharp.estimate (qsharp_code, len=%d)", len(qsharp_code))
            _log_params_debug_hints(params)
            result = _call_with_timeout(lambda: qsharp.estimate(qsharp_code, params=params))
            raw = dict(result)

        else:
            raise AlgorithmInputError("No algorithm input provided.")

        elapsed = time.monotonic() - t0
        logger.info("run_estimation: completed in %.3fs", elapsed)
        _log_result(raw)
        return raw

    except (AlgorithmInputError, UnknownAlgorithmTemplateError):
        raise
    except Exception as exc:
        elapsed = time.monotonic() - t0
        logger.error("run_estimation failed after %.3fs: %s", elapsed, exc)
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
        from qsharp.estimator import LogicalCounts
    except ImportError as exc:
        raise EstimationFailedError(
            "The 'qsharp' package is not installed. "
            "Install it with: pip install qsharp"
        ) from exc

    # Set estimate type to frontier
    frontier_params = dict(params)
    frontier_params["estimateType"] = "frontier"

    logger.debug("run_frontier_estimation params: %s", json.dumps(frontier_params, default=str))
    try:
        if logical_counts is not None:
            lc = LogicalCounts(logical_counts)
            result = _call_with_timeout(lambda: lc.estimate(frontier_params))
            raw = dict(result)

        elif algorithm_template is not None:
            template = _get_template(algorithm_template)
            lc = LogicalCounts(template.logical_counts)
            result = _call_with_timeout(lambda: lc.estimate(frontier_params))
            raw = dict(result)

        elif qsharp_code is not None:
            result = _call_with_timeout(lambda: qsharp.estimate(qsharp_code, params=frontier_params))
            raw = dict(result)

        else:
            raise AlgorithmInputError("No algorithm input provided.")

        logger.debug("run_frontier_estimation: got %d frontier points", len(raw.get("items", [])))
        return raw

    except (AlgorithmInputError, UnknownAlgorithmTemplateError):
        raise
    except Exception as exc:
        logger.error("run_frontier_estimation failed: %s", exc)
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


def _log_params_debug_hints(params: dict) -> None:
    """Log hints about params that may affect estimation performance."""
    qec = params.get("qecScheme", {})
    overrides = [k for k in qec if k != "name"]
    if overrides:
        logger.debug(
            "run_estimation: QEC overrides present (%s) — "
            "may increase estimator search time",
            ", ".join(f"{k}={qec[k]!r}" for k in overrides),
        )
    constraints = params.get("constraints", {})
    if constraints:
        logger.debug("run_estimation: constraints=%s", json.dumps(constraints))
    qubit = params.get("qubitParams", {})
    qubit_overrides = [k for k in qubit if k != "name"]
    if qubit_overrides:
        logger.debug(
            "run_estimation: qubit overrides present (%s)",
            ", ".join(f"{k}={qubit[k]!r}" for k in qubit_overrides),
        )


def _log_result(raw: dict) -> None:
    """Log a compact summary of a successful estimation result."""
    try:
        phys = raw.get("physicalCounts", {})
        summary = phys.get("physicalQubits") or raw.get("physicalQubits")
        runtime = (phys.get("runtime") or raw.get("runtimeFormatted") or
                   raw.get("physicalCountsFormatted", {}).get("runtime"))
        logger.info("run_estimation result: physical_qubits=%s runtime=%s", summary, runtime)
    except Exception:
        logger.debug("run_estimation result: (could not parse summary)")


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
