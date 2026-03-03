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
