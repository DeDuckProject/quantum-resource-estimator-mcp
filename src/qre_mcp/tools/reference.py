"""Reference tools: list qubit models, QEC schemes, and algorithm templates."""

from __future__ import annotations

from qre_mcp.data.algorithm_templates import ALGORITHM_TEMPLATES, CATEGORY_DESCRIPTIONS, _TEMPLATE_DISCLAIMER
from qre_mcp.data.qec_schemes import QEC_SCHEMES
from qre_mcp.data.qubit_models import QUBIT_MODELS


def list_qubit_models() -> dict:
    """List all 6 predefined physical qubit models with properties and descriptions.

    Returns structured data for all models with gate times, error rates, compatible
    technologies, and guidance on which to use.
    """
    models = list(QUBIT_MODELS.values())
    return {
        "qubit_models": models,
        "count": len(models),
        "guidance": (
            "Choose a qubit model based on your target technology:\n"
            "- superconducting/spin qubits: qubit_gate_ns_e3 (realistic) or qubit_gate_ns_e4 (optimistic)\n"
            "- trapped-ion qubits: qubit_gate_us_e3 (realistic) or qubit_gate_us_e4 (optimistic)\n"
            "- topological/Majorana qubits: qubit_maj_ns_e4 or qubit_maj_ns_e6\n"
            "\nNote: Majorana models (qubit_maj_ns_*) only work with the floquet_code QEC scheme. "
            "All other models work with surface_code."
        ),
    }


def list_qec_schemes() -> dict:
    """List available Quantum Error Correction schemes with compatibility info.

    Returns scheme parameters, compatible qubit models, and guidance on selection.
    """
    schemes = list(QEC_SCHEMES.values())
    return {
        "qec_schemes": schemes,
        "count": len(schemes),
        "guidance": (
            "Choose a QEC scheme based on your qubit model:\n"
            "- surface_code: works with all 6 qubit models. The standard choice.\n"
            "- floquet_code: only works with Majorana qubits (qubit_maj_ns_e4, qubit_maj_ns_e6). "
            "Offers better qubit overhead for Majorana hardware."
        ),
    }


def list_algorithm_templates() -> dict:
    """List predefined algorithm templates with logical resource counts.

    Templates cover common quantum algorithms with counts sourced from published research.
    Each template can be used directly with estimate_resources(algorithm_template=<id>).
    """
    templates = []
    for t in ALGORITHM_TEMPLATES.values():
        templates.append({
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "category": t.category,
            "logical_counts": t.logical_counts,
            "parameters": t.parameters,
            "source": t.source,
            "notes": t.notes,
            "caveats": list(t.caveats),
        })

    by_category: dict[str, list] = {}
    for t in templates:
        cat = t["category"]
        by_category.setdefault(cat, []).append(t)

    return {
        "disclaimer": _TEMPLATE_DISCLAIMER,
        "templates": templates,
        "count": len(templates),
        "categories": {
            cat: {"description": CATEGORY_DESCRIPTIONS.get(cat, ""), "templates": items}
            for cat, items in by_category.items()
        },
        "usage": (
            "Pass an algorithm template id to estimate_resources() using the "
            "'algorithm_template' parameter. Example: estimate_resources(algorithm_template='shor_2048')"
        ),
    }
