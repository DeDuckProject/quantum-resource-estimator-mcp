"""Integration tests: call the real qsharp estimator.

Run with:
    pytest -m integration -v -s

These tests are intentionally excluded from the default test run because they
call the actual qsharp resource estimator, which can take tens of seconds for
large templates.
"""

import time

import pytest

from qre_mcp.errors import EstimationFailedError, NoFeasibleSolutionError
from qre_mcp.tools.estimate import estimate_resources


@pytest.mark.integration
def test_shor_2048_with_cycle_time_override():
    """Reproduce the slow LLM request: shor_2048 + logicalCycleTime='1000 ns'.

    This is the exact request that was observed to hang. Running it here lets
    us measure wall-clock time and confirm whether the slowness is reproducible
    and how long it actually takes.
    """
    t0 = time.monotonic()
    result = estimate_resources(
        algorithm_template="shor_2048",
        qubit_model="qubit_gate_ns_e3",
        qec_scheme="surface_code",
        error_budget=0.001,
        qec_logical_cycle_time="1000 ns",
    )
    elapsed = time.monotonic() - t0

    print(f"\n[shor_2048 + cycle_time=1000ns] elapsed: {elapsed:.1f}s")
    print(f"  physical_qubits : {result['summary']['physical_qubits']}")
    print(f"  runtime         : {result['summary']['runtime']}")
    print(f"  code_distance   : {result['summary']['code_distance']}")

    assert "summary" in result
    assert result["summary"]["physical_qubits"] > 0


@pytest.mark.integration
def test_shor_2048_with_cycle_time_and_max_qubits_below_required():
    """Regression: shor_2048 + logicalCycleTime=1000ns + maxPhysicalQubits=20M.

    The unconstrained solution requires ~25.9M qubits.  Constraining to 20M
    with a custom logicalCycleTime used to cause the estimator to hang
    indefinitely.  After the timeout fix this must complete within the timeout
    and raise a well-typed error instead.
    """
    t0 = time.monotonic()
    with pytest.raises((EstimationFailedError, NoFeasibleSolutionError)) as exc_info:
        estimate_resources(
            algorithm_template="shor_2048",
            qubit_model="qubit_gate_ns_e3",
            qec_scheme="surface_code",
            error_budget=0.001,
            qec_logical_cycle_time="1000 ns",
            max_physical_qubits=20_000_000,
        )
    elapsed = time.monotonic() - t0

    print(f"\n[shor_2048 + cycle_time=1000ns + max_qubits=20M] elapsed: {elapsed:.1f}s")
    print(f"  raised: {type(exc_info.value).__name__}: {exc_info.value}")

    # Must not hang — the timeout cap is 60 s, add a small buffer
    assert elapsed < 70, f"estimation took {elapsed:.1f}s — timeout did not fire"


@pytest.mark.integration
def test_shor_2048_with_reaction_time():
    """shor_2048 + reaction_time='10 us' should produce reaction_limited=True.

    With a logical cycle time of ~1 µs and reaction time of 10 µs, the
    reaction time dominates and the adjusted runtime should be ~10x the original.
    """
    t0 = time.monotonic()
    result = estimate_resources(
        algorithm_template="shor_2048",
        qubit_model="qubit_gate_ns_e3",
        qec_scheme="surface_code",
        error_budget=0.001,
        qec_logical_cycle_time="1000 ns",
        reaction_time="10 us",
    )
    elapsed = time.monotonic() - t0

    summary = result["summary"]
    print(f"\n[shor_2048 + reaction_time=10us] elapsed: {elapsed:.1f}s")
    print(f"  physical_qubits              : {summary['physical_qubits']}")
    print(f"  runtime (original)           : {summary['runtime']}")
    print(f"  reaction_time_adjusted_runtime: {summary.get('reaction_time_adjusted_runtime')}")
    print(f"  reaction_limited             : {summary.get('reaction_limited')}")
    print(f"  reaction_time_note           : {summary.get('reaction_time_note')}")

    assert summary["reaction_limited"] is True
    assert summary["reaction_time_adjusted_runtime"] is not None
    assert summary["physical_qubits"] > 0


@pytest.mark.integration
def test_shor_2048_baseline_no_overrides():
    """Baseline: shor_2048 with default params (no QEC overrides).

    Used as a timing comparison against test_shor_2048_with_cycle_time_override
    to confirm that the cycle_time override is what causes the slowdown.
    """
    t0 = time.monotonic()
    result = estimate_resources(
        algorithm_template="shor_2048",
        qubit_model="qubit_gate_ns_e3",
        qec_scheme="surface_code",
        error_budget=0.001,
    )
    elapsed = time.monotonic() - t0

    print(f"\n[shor_2048 baseline] elapsed: {elapsed:.1f}s")
    print(f"  physical_qubits : {result['summary']['physical_qubits']}")
    print(f"  runtime         : {result['summary']['runtime']}")
    print(f"  code_distance   : {result['summary']['code_distance']}")

    assert "summary" in result
    assert result["summary"]["physical_qubits"] > 0
