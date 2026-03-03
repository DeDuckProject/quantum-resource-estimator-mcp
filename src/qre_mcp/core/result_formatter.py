"""Transforms raw qsharp estimator output into LLM-friendly structured responses."""

from __future__ import annotations

from typing import Any


def format_single_result(raw: dict[str, Any]) -> dict[str, Any]:
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
