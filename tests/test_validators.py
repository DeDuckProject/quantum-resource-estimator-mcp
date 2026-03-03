"""Tests for input validation."""

import pytest

from qre_mcp.core.validators import (
    validate_algorithm_input,
    validate_error_budget,
    validate_logical_counts,
    validate_qubit_model,
    validate_qubit_model_qec_compatibility,
)
from qre_mcp.errors import (
    AlgorithmInputError,
    IncompatibleQECSchemeError,
    InvalidErrorBudgetError,
    InvalidQubitModelError,
)


def test_validate_qubit_model_valid():
    validate_qubit_model("qubit_gate_ns_e3")  # should not raise


def test_validate_qubit_model_invalid():
    with pytest.raises(InvalidQubitModelError, match="Unknown qubit model"):
        validate_qubit_model("qubit_fictional_e9")


def test_validate_qec_compatibility_floquet_with_gate_based():
    with pytest.raises(IncompatibleQECSchemeError, match="only compatible with Majorana"):
        validate_qubit_model_qec_compatibility("qubit_gate_ns_e3", "floquet_code")


def test_validate_qec_compatibility_floquet_with_majorana():
    validate_qubit_model_qec_compatibility("qubit_maj_ns_e4", "floquet_code")  # ok


def test_validate_qec_compatibility_surface_with_all():
    for model in ["qubit_gate_ns_e3", "qubit_gate_us_e3", "qubit_maj_ns_e4"]:
        validate_qubit_model_qec_compatibility(model, "surface_code")  # all ok


def test_validate_error_budget_valid():
    validate_error_budget(0.001)
    validate_error_budget(0.01)
    validate_error_budget(0.1)


def test_validate_error_budget_out_of_range():
    with pytest.raises(InvalidErrorBudgetError):
        validate_error_budget(0.0)
    with pytest.raises(InvalidErrorBudgetError):
        validate_error_budget(1.0)
    with pytest.raises(InvalidErrorBudgetError):
        validate_error_budget(1.5)


def test_validate_error_budget_components_exceed_one():
    with pytest.raises(InvalidErrorBudgetError, match="sum of error budget components"):
        validate_error_budget(0.001, logical=0.5, t_states=0.5, rotations=0.5)


def test_validate_algorithm_input_exactly_one():
    validate_algorithm_input(None, "shor_2048", None)  # ok
    validate_algorithm_input(None, None, {"numQubits": 10})  # ok
    validate_algorithm_input("Q# code", None, None)  # ok


def test_validate_algorithm_input_none():
    with pytest.raises(AlgorithmInputError, match="No algorithm input"):
        validate_algorithm_input(None, None, None)


def test_validate_algorithm_input_multiple():
    with pytest.raises(AlgorithmInputError, match="Multiple algorithm inputs"):
        validate_algorithm_input(None, "shor_2048", {"numQubits": 10})


def test_validate_logical_counts_missing_num_qubits():
    with pytest.raises(AlgorithmInputError, match="numQubits"):
        validate_logical_counts({"tCount": 100})


def test_validate_logical_counts_zero_qubits():
    with pytest.raises(AlgorithmInputError, match="positive integer"):
        validate_logical_counts({"numQubits": 0})
