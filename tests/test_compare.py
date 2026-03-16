"""Tests for compare_configurations validation and config-building logic."""

from unittest.mock import patch

import pytest

from qre_mcp.errors import (
    AlgorithmInputError,
    IncompatibleQECSchemeError,
    InvalidQubitModelError,
)
from qre_mcp.tools.compare import compare_configurations


def _mock_batch(return_value=None):
    """Context managers that suppress the qsharp calls."""
    if return_value is None:
        return_value = []
    run = patch("qre_mcp.tools.compare.run_batch_estimation", return_value=return_value)
    fmt = patch("qre_mcp.tools.compare.format_batch_results", return_value={})
    return run, fmt


def test_no_algorithm_raises():
    with pytest.raises(AlgorithmInputError):
        compare_configurations()


def test_invalid_qubit_model_in_list_raises():
    with pytest.raises(InvalidQubitModelError):
        compare_configurations(
            algorithm_template="shor_2048",
            qubit_models=["fictional_model"],
        )


def test_floquet_with_gate_model_in_list_raises():
    with pytest.raises(IncompatibleQECSchemeError):
        compare_configurations(
            algorithm_template="shor_2048",
            qubit_models=["qubit_gate_ns_e3"],
            qec_scheme="floquet_code",
        )


def test_invalid_qubit_model_in_configurations_raises():
    with pytest.raises(InvalidQubitModelError):
        compare_configurations(
            algorithm_template="shor_2048",
            configurations=[{"qubit_model": "fictional_model"}],
        )


def test_compare_all_models_surface_code_uses_six_configs():
    run, fmt = _mock_batch()
    with run as mock_run, fmt:
        compare_configurations(algorithm_template="shor_2048", compare_all_models=True)
    _, _, _, params_list = mock_run.call_args[0]
    assert len(params_list) == 6


def test_compare_all_models_floquet_uses_two_configs():
    run, fmt = _mock_batch()
    with run as mock_run, fmt:
        compare_configurations(
            algorithm_template="shor_2048",
            compare_all_models=True,
            qec_scheme="floquet_code",
        )
    _, _, _, params_list = mock_run.call_args[0]
    assert len(params_list) == 2


def test_compare_specific_qubit_models():
    run, fmt = _mock_batch()
    with run as mock_run, fmt:
        compare_configurations(
            algorithm_template="shor_2048",
            qubit_models=["qubit_gate_ns_e3", "qubit_gate_us_e3"],
        )
    _, _, _, params_list = mock_run.call_args[0]
    assert len(params_list) == 2


def test_default_compare_uses_four_gate_based_models():
    run, fmt = _mock_batch()
    with run as mock_run, fmt:
        compare_configurations(algorithm_template="shor_2048")
    _, _, _, params_list = mock_run.call_args[0]
    assert len(params_list) == 4


def test_custom_configurations_passed_through():
    configs = [
        {"qubit_model": "qubit_gate_ns_e3", "qec_scheme": "surface_code", "error_budget": 0.001},
        {"qubit_model": "qubit_gate_us_e3", "qec_scheme": "surface_code", "error_budget": 0.01},
    ]
    run, fmt = _mock_batch()
    with run as mock_run, fmt:
        compare_configurations(algorithm_template="shor_2048", configurations=configs)
    _, _, _, params_list = mock_run.call_args[0]
    assert len(params_list) == 2
    assert params_list[0]["qubitParams"]["name"] == "qubit_gate_ns_e3"
    assert params_list[1]["errorBudget"] == 0.01
