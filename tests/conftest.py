"""Shared test fixtures."""

import pytest


MOCK_ESTIMATION_RESULT = {
    "physicalCounts": {
        "physicalQubits": 25344,
        "breakdown": {
            "algorithmicLogicalQubits": 25,
            "numTfactories": 14,
            "algorithmicLogicalDepth": 1_000_000,
        },
    },
    "physicalCountsFormatted": {
        "physicalQubits": "25,344",
        "runtime": "4 hours 22 mins",
        "rqops": "186",
    },
    "logicalQubit": {
        "codeDistance": 15,
        "physicalQubits": 450,
        "logicalCycleTime": "900 ns",
        "logicalErrorRate": 1e-12,
    },
    "tfactory": {
        "physicalQubits": 900,
        "runtime": "6.2 μs",
        "numRounds": 2,
        "numInputTstates": 15,
    },
    "logicalCounts": {
        "numQubits": 25,
        "tCount": 0,
        "rotationCount": 0,
        "cczCount": 1_000_000,
        "measurementCount": 5_000_000,
    },
    "jobParams": {
        "qubitParams": {"name": "qubit_gate_ns_e3"},
        "qecScheme": {"name": "surface_code"},
        "errorBudget": 0.001,
    },
}


@pytest.fixture
def mock_estimation_result():
    return MOCK_ESTIMATION_RESULT
