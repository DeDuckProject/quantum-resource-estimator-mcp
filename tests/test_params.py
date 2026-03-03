"""Tests for parameter building."""

from qre_mcp.core.params import all_qubit_model_configs, build_params_dict, build_params_list


def test_build_params_dict_defaults():
    params = build_params_dict()
    assert params["qubitParams"]["name"] == "qubit_gate_ns_e3"
    assert params["qecScheme"]["name"] == "surface_code"
    assert params["errorBudget"] == 0.001
    assert "constraints" not in params


def test_build_params_dict_with_constraints():
    params = build_params_dict(max_duration="1 hour", max_t_factories=10)
    assert params["constraints"]["maxDuration"] == "1 hour"
    assert params["constraints"]["maxTFactories"] == 10
    assert "maxPhysicalQubits" not in params["constraints"]


def test_build_params_dict_with_error_budget_breakdown():
    params = build_params_dict(
        error_budget_logical=0.0005,
        error_budget_t_states=0.0003,
        error_budget_rotations=0.0002,
    )
    budget = params["errorBudget"]
    assert isinstance(budget, dict)
    assert budget["logical"] == 0.0005
    assert budget["tStates"] == 0.0003
    assert budget["rotations"] == 0.0002


def test_build_params_list():
    configs = [
        {"qubit_model": "qubit_gate_ns_e3"},
        {"qubit_model": "qubit_gate_us_e3", "error_budget": 0.01},
    ]
    params_list = build_params_list(configs)
    assert len(params_list) == 2
    assert params_list[0]["qubitParams"]["name"] == "qubit_gate_ns_e3"
    assert params_list[1]["qubitParams"]["name"] == "qubit_gate_us_e3"
    assert params_list[1]["errorBudget"] == 0.01


def test_all_qubit_model_configs_surface_code():
    configs = all_qubit_model_configs(qec_scheme="surface_code")
    assert len(configs) == 6  # all models compatible with surface_code


def test_all_qubit_model_configs_floquet_code():
    configs = all_qubit_model_configs(qec_scheme="floquet_code")
    assert len(configs) == 2  # only Majorana models
    model_ids = {c["qubit_model"] for c in configs}
    assert model_ids == {"qubit_maj_ns_e4", "qubit_maj_ns_e6"}


# --- qubit_model_overrides ---

def test_build_params_dict_single_qubit_override():
    params = build_params_dict(qubit_model_overrides={"twoQubitGateTime": "10 ns"})
    assert params["qubitParams"]["name"] == "qubit_gate_ns_e3"
    assert params["qubitParams"]["twoQubitGateTime"] == "10 ns"


def test_build_params_dict_multiple_qubit_overrides():
    overrides = {"twoQubitGateTime": "10 ns", "oneQubitGateErrorRate": 1e-4}
    params = build_params_dict(qubit_model_overrides=overrides)
    assert params["qubitParams"]["twoQubitGateTime"] == "10 ns"
    assert params["qubitParams"]["oneQubitGateErrorRate"] == 1e-4
    assert params["qubitParams"]["name"] == "qubit_gate_ns_e3"


def test_build_params_dict_no_overrides_backward_compat():
    params = build_params_dict()
    assert params["qubitParams"] == {"name": "qubit_gate_ns_e3"}
    assert params["qecScheme"] == {"name": "surface_code"}


# --- QEC scheme overrides ---

def test_build_params_dict_qec_crossing_prefactor_only():
    params = build_params_dict(qec_crossing_prefactor=0.1)
    assert params["qecScheme"]["name"] == "surface_code"
    assert params["qecScheme"]["crossingPrefactor"] == 0.1
    assert "errorCorrectionThreshold" not in params["qecScheme"]


def test_build_params_dict_all_qec_params():
    params = build_params_dict(
        qec_crossing_prefactor=0.03,
        qec_error_correction_threshold=0.01,
        qec_logical_cycle_time="1000 ns",
        qec_physical_qubits_per_logical="2 * codeDistance * codeDistance",
    )
    qec = params["qecScheme"]
    assert qec["crossingPrefactor"] == 0.03
    assert qec["errorCorrectionThreshold"] == 0.01
    assert qec["logicalCycleTime"] == "1000"
    assert qec["physicalQubitsPerLogicalQubit"] == "2 * codeDistance * codeDistance"


def test_build_params_dict_no_qec_params_backward_compat():
    params = build_params_dict()
    assert params["qecScheme"] == {"name": "surface_code"}


def test_build_params_list_mixed_configs():
    configs = [
        {"qubit_model": "qubit_gate_ns_e3"},
        {"qubit_model": "qubit_gate_us_e3", "qec_logical_cycle_time": "1000 ns"},
        {"qubit_model": "qubit_gate_ns_e4", "qubit_model_overrides": {"twoQubitGateTime": "10 ns"}},
    ]
    params_list = build_params_list(configs)
    assert len(params_list) == 3
    assert "logicalCycleTime" not in params_list[0]["qecScheme"]
    assert params_list[1]["qecScheme"]["logicalCycleTime"] == "1000"
    assert params_list[2]["qubitParams"]["twoQubitGateTime"] == "10 ns"
    assert params_list[2]["qubitParams"]["name"] == "qubit_gate_ns_e4"


# --- _parse_cycle_time ---

from qre_mcp.core.params import _parse_cycle_time


def test_parse_cycle_time_ns():
    assert _parse_cycle_time("1000 ns") == "1000"


def test_parse_cycle_time_us():
    assert _parse_cycle_time("1 us") == "1000"
    assert _parse_cycle_time("1 µs") == "1000"


def test_parse_cycle_time_ms():
    assert _parse_cycle_time("0.5 ms") == "500000"


def test_parse_cycle_time_s():
    assert _parse_cycle_time("1 s") == "1000000000"


def test_parse_cycle_time_scientific():
    assert _parse_cycle_time("1e3 ns") == "1000"


def test_parse_cycle_time_formula_passthrough():
    # Formula expressions must be left unchanged
    assert _parse_cycle_time("4 * oneQubitMeasurementTime") == "4 * oneQubitMeasurementTime"


def test_build_params_dict_cycle_time_ns_converted():
    # End-to-end: "1000 ns" should reach qsharp as "1000"
    params = build_params_dict(qec_logical_cycle_time="1000 ns")
    assert params["qecScheme"]["logicalCycleTime"] == "1000"


def test_build_params_dict_cycle_time_us_converted():
    params = build_params_dict(qec_logical_cycle_time="1 us")
    assert params["qecScheme"]["logicalCycleTime"] == "1000"
