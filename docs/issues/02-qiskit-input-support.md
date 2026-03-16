## Title
feat: support Qiskit `QuantumCircuit` as algorithm input

## Labels
`enhancement`, `feature-request`

## Body

### Summary

Microsoft's QRE accepts Qiskit `QuantumCircuit` objects as input via `qsharp.interop.qiskit`. The MCP currently only accepts Q# code strings, logical counts, or predefined templates — leaving the large Qiskit user base without a direct path to resource estimation.

### What Microsoft's QRE supports

```python
from qsharp.interop.qiskit import estimate
from qiskit import QuantumCircuit

qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 1)
# ...

result = estimate(qc, params={"qubitParams": {"name": "qubit_gate_ns_e3"}})
```

Alternatively via the `ResourceEstimatorBackend`:

```python
from qsharp.interop.qiskit import ResourceEstimatorBackend
backend = ResourceEstimatorBackend()
job = backend.run(qc)
result = job.result()
```

Qiskit circuits are transpiled to QIR (Quantum Intermediate Representation) before being passed to the estimator.

### What's currently missing

- No `qiskit_circuit` input path in any estimation tool
- `run_estimation` in `core/estimator.py` only handles `qsharp_code`, `algorithm_template`, or `logical_counts`
- No mention of Qiskit in documentation or `explain_parameters`

### Proposed solution

1. **Add a `qiskit_circuit` parameter** to `estimate_resources`, `generate_frontier`, and `compare_configurations` — accepting a Qiskit `QuantumCircuit` object serialized as a JSON string (OpenQASM 3 or Qiskit's native JSON serialization).
2. **Add a conversion step** in `core/estimator.py` that deserializes the circuit and calls `qsharp.interop.qiskit.estimate()`.
3. **Make `qiskit` an optional dependency** — raise a clear `EstimationFailedError` if `qiskit` is not installed rather than crashing at import.
4. **Update `explain_parameters`** to document the Qiskit input path.

### Considerations

- Qiskit circuits are limited to the gate set supported by QIR transpilation; gates not in the universal set will need decomposition before estimation.
- This adds `qiskit` as an optional dependency — should be gated behind an extras marker in `pyproject.toml` (e.g., `pip install qre-mcp[qiskit]`).

### References

- [Azure Quantum: Use Qiskit with Resource Estimator](https://learn.microsoft.com/en-us/azure/quantum/how-to-submit-re-jobs)
- `qsharp.interop.qiskit` module in the `qsharp` Python package
