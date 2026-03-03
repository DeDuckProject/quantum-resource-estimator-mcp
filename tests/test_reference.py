"""Tests for reference tools (no qsharp dependency)."""

from qre_mcp.tools.reference import (
    list_algorithm_templates,
    list_qec_schemes,
    list_qubit_models,
)


def test_list_qubit_models_count():
    result = list_qubit_models()
    assert result["count"] == 6
    assert len(result["qubit_models"]) == 6


def test_list_qubit_models_has_required_fields():
    result = list_qubit_models()
    for model in result["qubit_models"]:
        assert "id" in model
        assert "name" in model
        assert "technology" in model
        assert "description" in model
        assert "one_qubit_gate_time" in model
        assert "two_qubit_gate_error_rate" in model


def test_list_qubit_models_ids():
    result = list_qubit_models()
    ids = {m["id"] for m in result["qubit_models"]}
    expected = {
        "qubit_gate_ns_e3", "qubit_gate_ns_e4",
        "qubit_gate_us_e3", "qubit_gate_us_e4",
        "qubit_maj_ns_e4", "qubit_maj_ns_e6",
    }
    assert ids == expected


def test_list_qec_schemes_count():
    result = list_qec_schemes()
    assert result["count"] == 2
    assert len(result["qec_schemes"]) == 2


def test_list_qec_schemes_has_required_fields():
    result = list_qec_schemes()
    for scheme in result["qec_schemes"]:
        assert "id" in scheme
        assert "name" in scheme
        assert "description" in scheme
        assert "compatible_instruction_sets" in scheme


def test_floquet_code_majorana_only():
    result = list_qec_schemes()
    floquet = next(s for s in result["qec_schemes"] if s["id"] == "floquet_code")
    assert floquet["compatible_instruction_sets"] == ["Majorana"]


def test_surface_code_universal():
    result = list_qec_schemes()
    surface = next(s for s in result["qec_schemes"] if s["id"] == "surface_code")
    assert "GateBased" in surface["compatible_instruction_sets"]
    assert "Majorana" in surface["compatible_instruction_sets"]


def test_list_algorithm_templates_count():
    result = list_algorithm_templates()
    assert result["count"] == 4
    assert len(result["templates"]) == 4


def test_list_algorithm_templates_ids():
    result = list_algorithm_templates()
    ids = {t["id"] for t in result["templates"]}
    assert "shor_2048" in ids
    assert "grover_aes128" in ids
    assert "chemistry_femo" in ids
    assert "qpe_generic" in ids


def test_list_algorithm_templates_has_logical_counts():
    result = list_algorithm_templates()
    for template in result["templates"]:
        assert "logical_counts" in template
        assert "numQubits" in template["logical_counts"]
        assert template["logical_counts"]["numQubits"] > 0


def test_list_algorithm_templates_has_source():
    result = list_algorithm_templates()
    for template in result["templates"]:
        assert "source" in template
        assert len(template["source"]) > 0
