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
