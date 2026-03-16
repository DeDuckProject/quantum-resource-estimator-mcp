"""Tests for server-level JSON parsing and MCP tool registration."""

import pytest

from qre_mcp.server import _parse_json, mcp


# ---------------------------------------------------------------------------
# _parse_json helper
# ---------------------------------------------------------------------------


def test_parse_json_valid_object():
    result = _parse_json('{"numQubits": 100, "tCount": 200}', "logical_counts")
    assert result == {"numQubits": 100, "tCount": 200}


def test_parse_json_valid_list():
    result = _parse_json('[{"qubit_model": "qubit_gate_ns_e3"}]', "configurations")
    assert isinstance(result, list)
    assert result[0]["qubit_model"] == "qubit_gate_ns_e3"


def test_parse_json_invalid_raises_value_error():
    with pytest.raises(ValueError, match="logical_counts"):
        _parse_json("{not valid json}", "logical_counts")


def test_parse_json_invalid_includes_field_name():
    with pytest.raises(ValueError, match="qubit_model_overrides"):
        _parse_json("{'key': 'single quotes'}", "qubit_model_overrides")


def test_parse_json_empty_object():
    result = _parse_json("{}", "logical_counts")
    assert result == {}


# ---------------------------------------------------------------------------
# MCP tool registration
# ---------------------------------------------------------------------------


def test_all_expected_tools_registered():
    tool_names = {t.name for t in mcp._tool_manager._tools.values()}
    expected = {
        "estimate_resources",
        "compare_configurations",
        "generate_frontier",
        "list_qubit_models",
        "list_qec_schemes",
        "list_algorithm_templates",
        "explain_parameters",
        "custom_qubit_model_estimate",
    }
    assert expected.issubset(tool_names)


def test_expected_resources_registered():
    resource_uris = set(mcp._resource_manager._resources.keys())
    assert "qre://qubit-models" in resource_uris
    assert "qre://algorithm-catalog" in resource_uris


def test_expected_prompts_registered():
    prompt_names = set(mcp._prompt_manager._prompts.keys())
    assert "guided_estimation" in prompt_names
    assert "architecture_comparison" in prompt_names
