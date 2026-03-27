"""Tests for result formatting."""

from qre_mcp.core.result_formatter import (
    format_batch_results,
    format_frontier_results,
    format_single_result,
)


def test_format_single_result_summary_keys(mock_estimation_result):
    result = format_single_result(mock_estimation_result)
    assert "summary" in result
    assert "details" in result
    summary = result["summary"]
    assert summary["physical_qubits"] == 25344
    assert summary["runtime"] == "4 hours 22 mins"
    assert summary["logical_qubits"] == 25
    assert summary["code_distance"] == 15
    assert summary["t_factory_copies"] == 14


def test_format_single_result_details(mock_estimation_result):
    result = format_single_result(mock_estimation_result)
    details = result["details"]
    assert "physical_counts" in details
    assert "logical_qubit" in details
    assert "t_factory" in details
    assert "job_params" in details


def test_format_batch_results(mock_estimation_result):
    configs = [
        {"qubit_model": "qubit_gate_ns_e3", "qec_scheme": "surface_code", "error_budget": 0.001},
        {"qubit_model": "qubit_gate_us_e3", "qec_scheme": "surface_code", "error_budget": 0.001},
    ]
    result = format_batch_results([mock_estimation_result, mock_estimation_result], configs)
    assert "comparison" in result
    assert len(result["comparison"]) == 2
    assert result["comparison"][0]["physical_qubits"] == 25344


def test_format_frontier_results_list(mock_estimation_result):
    frontier = format_frontier_results([mock_estimation_result, mock_estimation_result])
    assert "frontier" in frontier
    assert len(frontier["frontier"]) == 2


def test_format_frontier_results_single(mock_estimation_result):
    # Single result (no entries key, not a list)
    frontier = format_frontier_results(mock_estimation_result)
    assert "frontier" in frontier
    assert len(frontier["frontier"]) == 1


# --- Reaction-time adjustment tests ---


def test_reaction_time_limited(mock_estimation_result):
    """reaction_time > cycle_time => reaction_limited=True, adjusted runtime."""
    # Mock has logicalCycleTime="900 ns", algorithmicLogicalDepth=1_000_000
    # reaction_time = 10_000 ns (10 us) > 900 ns => reaction limited
    result = format_single_result(mock_estimation_result, reaction_time_ns=10_000.0)
    summary = result["summary"]
    assert summary["reaction_limited"] is True
    assert summary["reaction_time_adjusted_runtime"] is not None
    assert "reaction_time_note" in summary
    # effective_cycle = max(900, 10000) = 10000 ns
    # adjusted = 1_000_000 * 10_000 = 10_000_000_000 ns = 10 seconds
    assert "secs" in summary["reaction_time_adjusted_runtime"]


def test_reaction_time_not_limiting(mock_estimation_result):
    """reaction_time < cycle_time => reaction_limited=False."""
    # reaction_time = 500 ns < 900 ns => not limiting
    result = format_single_result(mock_estimation_result, reaction_time_ns=500.0)
    summary = result["summary"]
    assert summary["reaction_limited"] is False
    assert summary["reaction_time_adjusted_runtime"] is not None


def test_no_reaction_time(mock_estimation_result):
    """No reaction_time => no adjustment keys in summary."""
    result = format_single_result(mock_estimation_result)
    summary = result["summary"]
    assert "reaction_limited" not in summary
    assert "reaction_time_adjusted_runtime" not in summary
    assert "reaction_time_note" not in summary


def test_reaction_time_missing_depth():
    """Missing algorithmicLogicalDepth => graceful None + note."""
    raw = {
        "physicalCounts": {"physicalQubits": 100, "breakdown": {}},
        "physicalCountsFormatted": {},
        "logicalQubit": {"logicalCycleTime": "900 ns"},
        "tfactory": {},
        "logicalCounts": {},
        "jobParams": {},
    }
    result = format_single_result(raw, reaction_time_ns=10_000.0)
    summary = result["summary"]
    assert summary["reaction_limited"] is None
    assert summary["reaction_time_adjusted_runtime"] is None
    assert "not found" in summary["reaction_time_note"]


def test_reaction_time_missing_cycle_time():
    """Missing logicalCycleTime => graceful None + note."""
    raw = {
        "physicalCounts": {
            "physicalQubits": 100,
            "breakdown": {"algorithmicLogicalDepth": 1000},
        },
        "physicalCountsFormatted": {},
        "logicalQubit": {},
        "tfactory": {},
        "logicalCounts": {},
        "jobParams": {},
    }
    result = format_single_result(raw, reaction_time_ns=10_000.0)
    summary = result["summary"]
    assert summary["reaction_limited"] is None
    assert summary["reaction_time_adjusted_runtime"] is None
    assert "not found" in summary["reaction_time_note"]
