"""Transforms raw qsharp estimator output into LLM-friendly structured responses."""

from __future__ import annotations

from typing import Any

from qre_mcp.core.params import parse_duration_ns


def _format_duration_ns(ns: float) -> str:
    """Format a nanosecond value into a human-readable duration string."""
    if ns >= 3_600_000_000_000:
        hours = ns / 3_600_000_000_000
        return f"{hours:.2f} hours"
    if ns >= 60_000_000_000:
        mins = ns / 60_000_000_000
        return f"{mins:.2f} mins"
    if ns >= 1_000_000_000:
        secs = ns / 1_000_000_000
        return f"{secs:.2f} secs"
    if ns >= 1_000_000:
        ms = ns / 1_000_000
        return f"{ms:.2f} ms"
    if ns >= 1_000:
        us = ns / 1_000
        return f"{us:.2f} us"
    return f"{ns:.2f} ns"


def _apply_reaction_time_adjustment(
    summary: dict[str, Any],
    raw: dict[str, Any],
    reaction_time_ns: float,
) -> None:
    """Add reaction-time-adjusted runtime fields to summary (in-place).

    Reads algorithmicLogicalDepth and logicalCycleTime from the raw output,
    computes effective_cycle = max(cycle_time_ns, reaction_time_ns), and adds:
    - reaction_time_adjusted_runtime (human-readable string or None)
    - reaction_limited (bool or None)
    - reaction_time_note (explanation string)
    """
    depth = raw.get("physicalCounts", {}).get("breakdown", {}).get("algorithmicLogicalDepth")
    cycle_time_str = raw.get("logicalQubit", {}).get("logicalCycleTime")

    if depth is None or cycle_time_str is None:
        summary["reaction_time_adjusted_runtime"] = None
        summary["reaction_limited"] = None
        summary["reaction_time_note"] = (
            "Could not compute reaction-time adjustment: "
            "algorithmicLogicalDepth or logicalCycleTime not found in estimator output."
        )
        return

    # logicalCycleTime can be a string like "900 ns", a plain number string "1000",
    # or an actual int/float from the qsharp estimator output.
    if isinstance(cycle_time_str, (int, float)):
        cycle_time_ns = float(cycle_time_str)
    else:
        try:
            cycle_time_ns = parse_duration_ns(cycle_time_str)
        except ValueError:
            try:
                cycle_time_ns = float(cycle_time_str)
            except (ValueError, TypeError):
                summary["reaction_time_adjusted_runtime"] = None
                summary["reaction_limited"] = None
                summary["reaction_time_note"] = (
                    f"Could not parse logicalCycleTime '{cycle_time_str}' from estimator output."
                )
                return

    effective_cycle_ns = max(cycle_time_ns, reaction_time_ns)
    adjusted_runtime_ns = depth * effective_cycle_ns
    reaction_limited = reaction_time_ns > cycle_time_ns

    summary["reaction_time_adjusted_runtime"] = _format_duration_ns(adjusted_runtime_ns)
    summary["reaction_limited"] = reaction_limited
    summary["reaction_time_note"] = (
        f"Adjusted runtime using effective cycle time = max(logicalCycleTime={_format_duration_ns(cycle_time_ns)}, "
        f"reactionTime={_format_duration_ns(reaction_time_ns)}) = {_format_duration_ns(effective_cycle_ns)}. "
        f"algorithmicLogicalDepth={depth}. "
        f"{'Reaction time dominates (reaction_limited=True).' if reaction_limited else 'Logical cycle time dominates (reaction_limited=False).'}"
    )


def format_single_result(
    raw: dict[str, Any],
    reaction_time_ns: float | None = None,
) -> dict[str, Any]:
    """Format a single estimation result into a summary + details structure."""
    pf = raw.get("physicalCountsFormatted", {})
    pc = raw.get("physicalCounts", {})
    lq = raw.get("logicalQubit", {})
    tf = raw.get("tfactory", {})
    lc = raw.get("logicalCounts", {})
    jp = raw.get("jobParams", {})

    summary = {
        "physical_qubits": pc.get("physicalQubits"),
        "runtime": pf.get("runtime"),
        "logical_qubits": pc.get("breakdown", {}).get("algorithmicLogicalQubits"),
        "code_distance": lq.get("codeDistance"),
        "t_factory_copies": pc.get("breakdown", {}).get("numTfactories"),
        "rqops": pf.get("rqops"),
        "physical_qubits_formatted": pf.get("physicalQubits"),
    }

    if reaction_time_ns is not None:
        _apply_reaction_time_adjustment(summary, raw, reaction_time_ns)

    details = {
        "physical_counts": pc,
        "physical_counts_formatted": pf,
        "logical_qubit": lq,
        "t_factory": tf,
        "logical_counts": lc,
        "job_params": jp,
    }

    return {"summary": summary, "details": details}


def format_batch_results(raw_list: list[dict[str, Any]], configs: list[dict]) -> dict[str, Any]:
    """Format a list of estimation results for comparison."""
    rows = []
    for raw, cfg in zip(raw_list, configs):
        formatted = format_single_result(raw)
        rows.append({
            "configuration": {
                "qubit_model": cfg.get("qubit_model") or cfg.get("qubitParams", {}).get("name"),
                "qec_scheme": cfg.get("qec_scheme") or cfg.get("qecScheme", {}).get("name"),
                "error_budget": cfg.get("error_budget") or cfg.get("errorBudget"),
            },
            **formatted["summary"],
        })

    return {
        "comparison": rows,
        "note": (
            "physical_qubits and runtime are the primary metrics. "
            "code_distance indicates how much error correction overhead is applied."
        ),
    }


def format_frontier_results(raw: dict[str, Any]) -> dict[str, Any]:
    """Format Pareto frontier results (time vs qubits tradeoff)."""
    points = []
    if isinstance(raw, list):
        for item in raw:
            pf = item.get("physicalCountsFormatted", {})
            pc = item.get("physicalCounts", {})
            points.append({
                "physical_qubits": pc.get("physicalQubits"),
                "physical_qubits_formatted": pf.get("physicalQubits"),
                "runtime": pf.get("runtime"),
                "t_factory_copies": pc.get("breakdown", {}).get("numTfactories"),
                "code_distance": item.get("logicalQubit", {}).get("codeDistance"),
            })
    elif "entries" in raw:
        for item in raw["entries"]:
            pf = item.get("physicalCountsFormatted", {})
            pc = item.get("physicalCounts", {})
            points.append({
                "physical_qubits": pc.get("physicalQubits"),
                "physical_qubits_formatted": pf.get("physicalQubits"),
                "runtime": pf.get("runtime"),
                "t_factory_copies": pc.get("breakdown", {}).get("numTfactories"),
                "code_distance": item.get("logicalQubit", {}).get("codeDistance"),
            })
    else:
        # Single result returned when frontier has one point
        return {"frontier": [format_single_result(raw)["summary"]]}

    return {
        "frontier": points,
        "description": (
            "Each point is Pareto-optimal: you cannot reduce qubit count without "
            "increasing runtime, or reduce runtime without increasing qubit count. "
            "The first point minimizes qubits; the last minimizes runtime."
        ),
    }
