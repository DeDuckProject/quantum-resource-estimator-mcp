"""Quantum Resource Estimator MCP Server.

Exposes Microsoft QDK resource estimation via the Model Context Protocol,
enabling natural language resource estimation for quantum algorithms.
"""

from __future__ import annotations

import json
from typing import Any


def _parse_json(value: str, field_name: str) -> Any:
    """Parse a JSON string, raising ValueError with a clear message on failure."""
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON for '{field_name}': {e}") from e

from mcp.server.fastmcp import FastMCP

from qre_mcp._log import logger, setup_logging
from qre_mcp.data.algorithm_templates import ALGORITHM_TEMPLATES
from qre_mcp.data.qec_schemes import QEC_SCHEMES
from qre_mcp.data.qubit_models import QUBIT_MODELS
from qre_mcp.tools.compare import compare_configurations as _compare_configurations
from qre_mcp.tools.estimate import estimate_resources as _estimate_resources
from qre_mcp.tools.estimate import generate_frontier as _generate_frontier
from qre_mcp.tools.guidance import custom_qubit_model_estimate as _custom_qubit_model_estimate
from qre_mcp.tools.guidance import explain_parameters as _explain_parameters
from qre_mcp.tools.reference import list_algorithm_templates as _list_algorithm_templates
from qre_mcp.tools.reference import list_qec_schemes as _list_qec_schemes
from qre_mcp.tools.reference import list_qubit_models as _list_qubit_models

mcp = FastMCP(
    "Quantum Resource Estimator",
    instructions=(
        "This server provides quantum resource estimation using Microsoft's QDK. "
        "It helps you determine how many physical qubits and how much time are needed "
        "to run quantum algorithms on fault-tolerant hardware.\n\n"
        "Quick start:\n"
        "1. Use list_algorithm_templates() to see predefined algorithms.\n"
        "2. Use estimate_resources(algorithm_template='shor_2048') for a basic estimate.\n"
        "3. Use compare_configurations() to compare hardware architectures.\n"
        "4. Use explain_parameters(use_case='chemistry') for domain-specific guidance.\n"
        "5. Use generate_frontier() to explore the qubit-count vs. runtime tradeoff."
    ),
)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def estimate_resources(
    qsharp_code: str | None = None,
    algorithm_template: str | None = None,
    logical_counts: str | None = None,
    qubit_model: str = "qubit_gate_ns_e3",
    qec_scheme: str = "surface_code",
    error_budget: float = 0.001,
    max_duration: str | None = None,
    max_physical_qubits: int | None = None,
    max_t_factories: int | None = None,
    logical_depth_factor: float | None = None,
    error_budget_logical: float | None = None,
    error_budget_t_states: float | None = None,
    error_budget_rotations: float | None = None,
    qubit_model_overrides: str | None = None,
    qec_crossing_prefactor: float | None = None,
    qec_error_correction_threshold: float | None = None,
    qec_logical_cycle_time: str | None = None,
    qec_physical_qubits_per_logical: str | None = None,
) -> dict[str, Any]:
    """Estimate the physical quantum resources needed to run a quantum algorithm.

    Provide the algorithm as EXACTLY ONE of:
    - algorithm_template: ID of a predefined algorithm (e.g. 'shor_2048', 'grover_aes128',
      'chemistry_femo', 'qpe_generic'). Use list_algorithm_templates() for the full list.
    - logical_counts: JSON string with algorithm counts, e.g.:
      '{"numQubits": 100, "tCount": 200, "rotationCount": 50}'
    - qsharp_code: Q# source code string with a parameterless entry point operation.

    Hardware parameters:
    - qubit_model: Physical qubit technology. Default 'qubit_gate_ns_e3' (superconducting).
      Use list_qubit_models() for all options.
    - qec_scheme: Error correction scheme. 'surface_code' (default) or 'floquet_code'
      (Majorana qubits only).
    - error_budget: Acceptable failure probability (0-1). Default 0.001.
    - qubit_model_overrides: JSON string to override specific qubit parameters while keeping
      a named model as the base. E.g. '{"twoQubitGateTime": "10 ns"}'. Valid keys:
      oneQubitGateTime, twoQubitGateTime, oneQubitMeasurementTime, oneQubitGateErrorRate,
      twoQubitGateErrorRate, tGateErrorRate, readoutErrorRate, idleErrorRate.

    Optional QEC scheme overrides (override individual parameters of the named qec_scheme):
    - qec_crossing_prefactor: float > 0. Error-suppression prefactor (default ~0.03).
    - qec_error_correction_threshold: float in (0,1). Error correction threshold (default ~0.01).
    - qec_logical_cycle_time: Formula string for logical cycle duration, e.g. '1000 ns' for
      a fixed 1 µs cycle (replicates Gidney-Ekerå assumption).
    - qec_physical_qubits_per_logical: Formula string for qubits per logical qubit.

    Optional constraints (use at most one of max_duration or max_physical_qubits):
    - max_duration: e.g. '1 hour', '500 ms', '1 s'
    - max_physical_qubits: integer upper bound on qubit count
    - max_t_factories: limit T-factory copies (reduces qubits, increases runtime)
    - logical_depth_factor: multiplier on circuit depth (default 1.0)

    Returns: summary (physical_qubits, runtime, logical_qubits, code_distance, t_factory_copies)
    plus full details breakdown.
    """
    logger.info(
        "estimate_resources: template=%r model=%r qec=%r budget=%s overrides=%r "
        "cycle_time=%r max_duration=%r max_qubits=%r",
        algorithm_template, qubit_model, qec_scheme, error_budget,
        qubit_model_overrides, qec_logical_cycle_time, max_duration, max_physical_qubits,
    )
    counts_dict = _parse_json(logical_counts, "logical_counts") if logical_counts else None
    overrides_dict = _parse_json(qubit_model_overrides, "qubit_model_overrides") if qubit_model_overrides else None
    return _estimate_resources(
        qsharp_code=qsharp_code,
        algorithm_template=algorithm_template,
        logical_counts=counts_dict,
        qubit_model=qubit_model,
        qec_scheme=qec_scheme,
        error_budget=error_budget,
        max_duration=max_duration,
        max_physical_qubits=max_physical_qubits,
        max_t_factories=max_t_factories,
        logical_depth_factor=logical_depth_factor,
        error_budget_logical=error_budget_logical,
        error_budget_t_states=error_budget_t_states,
        error_budget_rotations=error_budget_rotations,
        qubit_model_overrides=overrides_dict,
        qec_crossing_prefactor=qec_crossing_prefactor,
        qec_error_correction_threshold=qec_error_correction_threshold,
        qec_logical_cycle_time=qec_logical_cycle_time,
        qec_physical_qubits_per_logical=qec_physical_qubits_per_logical,
    )


@mcp.tool()
def compare_configurations(
    algorithm_template: str | None = None,
    logical_counts: str | None = None,
    qsharp_code: str | None = None,
    qubit_models: list[str] | None = None,
    compare_all_models: bool = False,
    qec_scheme: str = "surface_code",
    error_budget: float = 0.001,
    configurations: str | None = None,
) -> dict[str, Any]:
    """Compare resource estimates across multiple hardware configurations.

    Provide the algorithm as exactly one of algorithm_template, logical_counts, or qsharp_code.

    Hardware selection (choose one approach):
    - compare_all_models=True: compare all compatible qubit models
    - qubit_models=['qubit_gate_ns_e3', 'qubit_gate_us_e3']: compare specific models
    - configurations: JSON string of full configs. Each config dict may include the standard
      qubit_model/qec_scheme/error_budget keys plus the new override keys:
      qubit_model_overrides (dict), qec_crossing_prefactor, qec_error_correction_threshold,
      qec_logical_cycle_time, qec_physical_qubits_per_logical. E.g.:
      '[{"qubit_model": "qubit_gate_ns_e3", "qec_logical_cycle_time": "1000 ns"}]'
    - Default (none specified): compare all 4 gate-based models

    Returns a side-by-side comparison table showing physical qubits, runtime, code distance,
    and T-factory copies for each configuration.
    """
    logger.info(
        "compare_configurations: template=%r model=%r qec=%r budget=%s "
        "compare_all=%s qubit_models=%r",
        algorithm_template, qec_scheme, qec_scheme, error_budget,
        compare_all_models, qubit_models,
    )
    counts_dict = _parse_json(logical_counts, "logical_counts") if logical_counts else None
    configs_list = _parse_json(configurations, "configurations") if configurations else None
    return _compare_configurations(
        qsharp_code=qsharp_code,
        algorithm_template=algorithm_template,
        logical_counts=counts_dict,
        qubit_models=qubit_models,
        compare_all_models=compare_all_models,
        qec_scheme=qec_scheme,
        error_budget=error_budget,
        configurations=configs_list,
    )


@mcp.tool()
def generate_frontier(
    algorithm_template: str | None = None,
    logical_counts: str | None = None,
    qsharp_code: str | None = None,
    qubit_model: str = "qubit_gate_ns_e3",
    qec_scheme: str = "surface_code",
    error_budget: float = 0.001,
    qubit_model_overrides: str | None = None,
    qec_crossing_prefactor: float | None = None,
    qec_error_correction_threshold: float | None = None,
    qec_logical_cycle_time: str | None = None,
    qec_physical_qubits_per_logical: str | None = None,
) -> dict[str, Any]:
    """Generate the Pareto frontier: qubit-count vs. runtime tradeoff for an algorithm.

    Provide the algorithm as exactly one of algorithm_template, logical_counts, or qsharp_code.

    Returns a list of Pareto-optimal points. Each point represents a configuration where
    you cannot reduce qubit count without increasing runtime, or vice versa.
    - First point: minimum qubit count (longest runtime)
    - Last point: minimum runtime (most qubits)

    Optional qubit/QEC overrides (same as estimate_resources):
    - qubit_model_overrides: JSON string to override specific qubit parameters.
    - qec_crossing_prefactor, qec_error_correction_threshold: float overrides.
    - qec_logical_cycle_time, qec_physical_qubits_per_logical: formula string overrides.

    Useful for understanding hardware requirements at different time budgets.
    """
    logger.info(
        "generate_frontier: template=%r model=%r qec=%r budget=%s overrides=%r cycle_time=%r",
        algorithm_template, qubit_model, qec_scheme, error_budget,
        qubit_model_overrides, qec_logical_cycle_time,
    )
    counts_dict = _parse_json(logical_counts, "logical_counts") if logical_counts else None
    overrides_dict = _parse_json(qubit_model_overrides, "qubit_model_overrides") if qubit_model_overrides else None
    return _generate_frontier(
        qsharp_code=qsharp_code,
        algorithm_template=algorithm_template,
        logical_counts=counts_dict,
        qubit_model=qubit_model,
        qec_scheme=qec_scheme,
        error_budget=error_budget,
        qubit_model_overrides=overrides_dict,
        qec_crossing_prefactor=qec_crossing_prefactor,
        qec_error_correction_threshold=qec_error_correction_threshold,
        qec_logical_cycle_time=qec_logical_cycle_time,
        qec_physical_qubits_per_logical=qec_physical_qubits_per_logical,
    )


@mcp.tool()
def list_qubit_models() -> dict[str, Any]:
    """List all 6 predefined physical qubit models with gate times, error rates, and descriptions.

    Returns information about:
    - qubit_gate_ns_e3/e4: Superconducting or spin qubits (nanosecond gates)
    - qubit_gate_us_e3/e4: Trapped-ion qubits (microsecond gates)
    - qubit_maj_ns_e4/e6: Majorana/topological qubits

    Use this to understand which qubit_model to select for estimate_resources().
    """
    return _list_qubit_models()


@mcp.tool()
def list_qec_schemes() -> dict[str, Any]:
    """List available Quantum Error Correction (QEC) schemes with compatibility notes.

    Returns details on:
    - surface_code: Works with all qubit models. The standard choice.
    - floquet_code: Majorana qubits only. Better overhead for topological hardware.

    Use this to understand which qec_scheme to select for estimate_resources().
    """
    return _list_qec_schemes()


@mcp.tool()
def list_algorithm_templates() -> dict[str, Any]:
    """List predefined quantum algorithm templates with logical resource counts.

    Templates are sourced from published research papers and cover:
    - cryptography: shor_2048, grover_aes128
    - chemistry: chemistry_femo
    - general: qpe_generic

    Each template can be passed directly to estimate_resources(algorithm_template=<id>).
    Returns logical resource counts (numQubits, cczCount, etc.) and source citations.
    """
    return _list_algorithm_templates()


@mcp.tool()
def explain_parameters(use_case: str | None = None) -> dict[str, Any]:
    """Explain resource estimation parameters and recommend configurations for a use case.

    If use_case is provided, gives targeted guidance. Valid values:
    - 'cryptography': guidance for quantum attacks on RSA, ECC, AES
    - 'chemistry': guidance for molecular simulation and drug discovery
    - 'optimization': guidance for combinatorial optimization
    - 'general': full parameter reference guide

    Returns parameter descriptions, recommended starting configurations, and relevant templates.
    """
    return _explain_parameters(use_case=use_case)


@mcp.tool()
def custom_qubit_model_estimate(
    algorithm_template: str | None = None,
    logical_counts: str | None = None,
    qsharp_code: str | None = None,
    instruction_set: str = "GateBased",
    one_qubit_gate_time: str = "50 ns",
    two_qubit_gate_time: str = "50 ns",
    one_qubit_measurement_time: str = "100 ns",
    one_qubit_gate_error_rate: float = 1e-3,
    two_qubit_gate_error_rate: float = 1e-3,
    t_gate_error_rate: float = 5e-4,
    readout_error_rate: float = 1e-3,
    idle_error_rate: float = 1e-4,
    qec_scheme: str = "surface_code",
    error_budget: float = 0.001,
) -> dict[str, Any]:
    """Estimate resources using fully custom physical qubit parameters.

    Use this when modeling novel hardware not covered by the 6 predefined qubit models.
    All gate times accept strings like '50 ns', '1 μs', '100 ms'.
    instruction_set: 'GateBased' (default) or 'Majorana'.

    Provide algorithm as exactly one of algorithm_template, logical_counts, or qsharp_code.
    """
    counts_dict = _parse_json(logical_counts, "logical_counts") if logical_counts else None
    return _custom_qubit_model_estimate(
        qsharp_code=qsharp_code,
        algorithm_template=algorithm_template,
        logical_counts=counts_dict,
        instruction_set=instruction_set,
        one_qubit_gate_time=one_qubit_gate_time,
        two_qubit_gate_time=two_qubit_gate_time,
        one_qubit_measurement_time=one_qubit_measurement_time,
        one_qubit_gate_error_rate=one_qubit_gate_error_rate,
        two_qubit_gate_error_rate=two_qubit_gate_error_rate,
        t_gate_error_rate=t_gate_error_rate,
        readout_error_rate=readout_error_rate,
        idle_error_rate=idle_error_rate,
        qec_scheme=qec_scheme,
        error_budget=error_budget,
    )


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


@mcp.resource("qre://qubit-models")
def qubit_models_resource() -> str:
    """Complete reference of all predefined physical qubit models."""
    data = _list_qubit_models()
    return json.dumps(data, indent=2)


@mcp.resource("qre://algorithm-catalog")
def algorithm_catalog_resource() -> str:
    """Catalog of predefined quantum algorithm templates with logical resource counts."""
    data = _list_algorithm_templates()
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------


@mcp.prompt()
def guided_estimation(algorithm_type: str = "general") -> str:
    """Step-by-step guided resource estimation prompt.

    Walks the user through: algorithm selection, hardware choice, QEC scheme,
    error budget, and optional constraints.
    """
    templates = list(ALGORITHM_TEMPLATES.keys())
    qubit_models = list(QUBIT_MODELS.keys())
    qec_schemes = list(QEC_SCHEMES.keys())

    return f"""You are helping a user perform quantum resource estimation using the Quantum Resource Estimator MCP server.

Guide them step by step through the following decisions. Ask one or two questions at a time.

**Step 1 — Algorithm**
Ask: What quantum algorithm do they want to estimate?
Available templates: {templates}
If none match, ask for logical resource counts (numQubits, tCount/cczCount, rotationCount).
If they want to provide Q# code, accept that too.

**Step 2 — Hardware (Qubit Model)**
Ask: What quantum hardware technology are they targeting?
Available models: {qubit_models}
Guidance:
- Superconducting / spin: qubit_gate_ns_e3 (realistic) or qubit_gate_ns_e4 (optimistic)
- Trapped-ion: qubit_gate_us_e3 (realistic) or qubit_gate_us_e4 (optimistic)
- Topological/Majorana: qubit_maj_ns_e4 or qubit_maj_ns_e6
- Default recommendation: qubit_gate_ns_e3

**Step 3 — QEC Scheme**
Available: {qec_schemes}
Note: floquet_code only works with Majorana qubits. Default: surface_code.

**Step 4 — Error Budget**
Ask: What failure probability is acceptable? Default: 0.001 (1 in 1000).
Lower = more conservative but requires more qubits.

**Step 5 — Constraints (Optional)**
Ask if they have hardware limits:
- Maximum physical qubits? (e.g. a specific quantum computer size)
- Maximum runtime? (e.g. '1 hour', '1 day')

**Step 6 — Run Estimation**
Once you have the parameters, call estimate_resources() and present the results clearly:
- Physical qubit count
- Runtime
- Code distance
- T-factory copies
Explain what each number means in plain language.

Algorithm type hint from user: {algorithm_type}
"""


@mcp.prompt()
def architecture_comparison(algorithm_description: str = "") -> str:
    """Structured analysis template for comparing quantum hardware architectures."""
    return f"""You are performing a quantum hardware architecture comparison for the following algorithm:

{algorithm_description if algorithm_description else "[Algorithm to be specified by user]"}

Use the Quantum Resource Estimator MCP server to perform a structured analysis.

**Analysis Steps:**

1. **Identify the algorithm**:
   - Call list_algorithm_templates() to check if a predefined template exists.
   - If not, ask the user for logical resource counts.

2. **Compare all architectures**:
   Call compare_configurations() with compare_all_models=True to get estimates for all qubit technologies.

3. **Generate Pareto frontiers** for the most promising architecture(s):
   Call generate_frontier() to show the qubit-count vs. runtime tradeoff.

4. **Structure your analysis** with these sections:

   ### Comparison Table
   Present the comparison results as a table with: Qubit Model | Technology | Physical Qubits | Runtime | Code Distance

   ### Key Observations
   - Which architecture requires the fewest qubits?
   - Which achieves the fastest runtime?
   - How do the tradeoffs differ between technologies?

   ### Feasibility Assessment
   - What physical qubit count is needed for each architecture?
   - Is any architecture feasible with near-term hardware (< 1 million qubits)?
   - What error rates are required?

   ### Recommendation
   - Best architecture for minimizing qubit count
   - Best architecture for minimizing runtime
   - Best overall for current technology trajectory

5. **Cite sources** for algorithm resource counts and contextualize against published projections.
"""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    setup_logging()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
