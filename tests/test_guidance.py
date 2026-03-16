"""Tests for explain_parameters and custom_qubit_model_estimate."""

from unittest.mock import patch

import pytest

from qre_mcp.errors import AlgorithmInputError
from qre_mcp.tools.guidance import custom_qubit_model_estimate, explain_parameters


# ---------------------------------------------------------------------------
# explain_parameters
# ---------------------------------------------------------------------------


def test_explain_parameters_no_use_case_returns_reference():
    result = explain_parameters()
    assert "parameter_reference" in result
    assert "available_use_cases" in result
    assert "qubit_model_options" in result
    assert "qec_scheme_options" in result


def test_explain_parameters_cryptography():
    result = explain_parameters(use_case="cryptography")
    assert result["use_case"] == "cryptography"
    assert "guidance" in result
    assert "shor_2048" in result["guidance"]["relevant_templates"]
    assert "grover_aes128" in result["guidance"]["relevant_templates"]


def test_explain_parameters_chemistry():
    result = explain_parameters(use_case="chemistry")
    assert result["use_case"] == "chemistry"
    assert "chemistry_femo" in result["guidance"]["relevant_templates"]


def test_explain_parameters_optimization():
    result = explain_parameters(use_case="optimization")
    assert result["use_case"] == "optimization"
    assert "guidance" in result


def test_explain_parameters_general():
    result = explain_parameters(use_case="general")
    assert "guidance" in result
    assert "workflow" in result["guidance"]


def test_explain_parameters_unknown_falls_back_to_general():
    result = explain_parameters(use_case="unknown_domain_xyz")
    # Falls back to general guidance, which has a workflow key
    assert "guidance" in result
    assert "workflow" in result["guidance"]


def test_explain_parameters_case_insensitive():
    result = explain_parameters(use_case="CRYPTOGRAPHY")
    assert "guidance" in result
    assert "shor_2048" in result["guidance"]["relevant_templates"]


def test_explain_parameters_includes_qubit_options():
    result = explain_parameters(use_case="chemistry")
    assert "qubit_gate_ns_e3" in result["qubit_model_options"]
    assert "surface_code" in result["qec_scheme_options"]


# ---------------------------------------------------------------------------
# custom_qubit_model_estimate
# ---------------------------------------------------------------------------


def test_custom_qubit_model_no_algorithm_raises():
    with pytest.raises(AlgorithmInputError):
        custom_qubit_model_estimate()


def _fake_run_estimation(qsharp_code, template, counts, params):
    return {
        "physicalCounts": {"physicalQubits": 1000, "breakdown": {}},
        "physicalCountsFormatted": {"physicalQubits": "1,000", "runtime": "1 s"},
        "logicalQubit": {"codeDistance": 5, "physicalQubits": 50, "logicalCycleTime": "100 ns"},
        "logicalCounts": {"numQubits": 10},
    }


def test_custom_qubit_model_cycle_time_parsed():
    """Regression: '1000 ns' must be converted to '1000' before reaching qsharp."""
    captured = {}

    def fake_run(qsharp_code, template, counts, params):
        captured.update(params)
        return _fake_run_estimation(qsharp_code, template, counts, params)

    with patch("qre_mcp.tools.guidance.run_estimation", side_effect=fake_run), \
         patch("qre_mcp.tools.guidance.format_single_result", return_value={}):
        custom_qubit_model_estimate(
            algorithm_template="qpe_generic",
            qec_logical_cycle_time="1000 ns",
        )

    assert captured["qecScheme"]["logicalCycleTime"] == "1000"


def test_custom_qubit_model_cycle_time_us_parsed():
    captured = {}

    def fake_run(qsharp_code, template, counts, params):
        captured.update(params)
        return _fake_run_estimation(qsharp_code, template, counts, params)

    with patch("qre_mcp.tools.guidance.run_estimation", side_effect=fake_run), \
         patch("qre_mcp.tools.guidance.format_single_result", return_value={}):
        custom_qubit_model_estimate(
            algorithm_template="qpe_generic",
            qec_logical_cycle_time="1 us",
        )

    assert captured["qecScheme"]["logicalCycleTime"] == "1000"


def test_custom_qubit_model_cycle_time_formula_passthrough():
    """Formula expressions must not be modified."""
    captured = {}
    formula = "4 * twoQubitGateTime * codeDistance"

    def fake_run(qsharp_code, template, counts, params):
        captured.update(params)
        return _fake_run_estimation(qsharp_code, template, counts, params)

    with patch("qre_mcp.tools.guidance.run_estimation", side_effect=fake_run), \
         patch("qre_mcp.tools.guidance.format_single_result", return_value={}):
        custom_qubit_model_estimate(
            algorithm_template="qpe_generic",
            qec_logical_cycle_time=formula,
        )

    assert captured["qecScheme"]["logicalCycleTime"] == formula


def test_custom_qubit_model_passes_custom_params():
    captured = {}

    def fake_run(qsharp_code, template, counts, params):
        captured.update(params)
        return _fake_run_estimation(qsharp_code, template, counts, params)

    with patch("qre_mcp.tools.guidance.run_estimation", side_effect=fake_run), \
         patch("qre_mcp.tools.guidance.format_single_result", return_value={}):
        custom_qubit_model_estimate(
            algorithm_template="qpe_generic",
            one_qubit_gate_time="20 ns",
            two_qubit_gate_time="40 ns",
            one_qubit_gate_error_rate=1e-4,
        )

    qubit = captured["qubitParams"]
    assert qubit["oneQubitGateTime"] == "20 ns"
    assert qubit["twoQubitGateTime"] == "40 ns"
    assert qubit["oneQubitGateErrorRate"] == 1e-4
