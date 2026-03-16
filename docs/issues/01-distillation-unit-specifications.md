## Title
feat: support `distillationUnitSpecifications` for custom T-factory distillation

## Labels
`enhancement`, `feature-request`

## Body

### Summary

The Microsoft QRE supports a `distillationUnitSpecifications` parameter that lets users specify custom T-factory distillation algorithms. This MCP currently has **no support** for this parameter, which is a significant gap for users who want to model custom or alternative distillation protocols.

### What Microsoft's QRE supports

The `distillationUnitSpecifications` field accepts a list of distillation unit specs, each with:

| Field | Type | Description |
|-------|------|-------------|
| `displayName` | string | Label shown in output |
| `numInputTs` | int | Number of input T states |
| `numOutputTs` | int | Number of output T states |
| `failureProbabilityFormula` | string | Formula for failure probability |
| `outputErrorRateFormula` | string | Formula for output error rate |
| `physicalQubitSpecification` | object | `{ numUnitQubits, durationInQubitCycleTime }` |
| `logicalQubitSpecification` | object | `{ numUnitQubits, durationInQubitCycleTime }` |
| `logicalQubitSpecificationFirstRoundOverride` | object | Override for first distillation round |

Predefined named options include `"15-1 RM"` and `"15-1 space-efficient"`.

### What's currently missing

- No `distillation_units` parameter in `estimate_resources`, `generate_frontier`, or `compare_configurations`
- No `list_distillation_units` reference tool
- No validation for distillation unit fields
- `build_params_dict` in `core/params.py` does not build `distillationUnitSpecifications`

### Proposed solution

1. **Add `distillation_units` parameter** to `estimate_resources`, `generate_frontier`, and `compare_configurations` — accepting a JSON string that maps to `distillationUnitSpecifications` in the qsharp params dict.
2. **Support predefined names** (e.g., `"15-1 RM"`) as a convenience shorthand.
3. **Add a `list_distillation_units` reference tool** listing known predefined options with descriptions.
4. **Add validation** in `core/validators.py` for the distillation unit schema.
5. **Update `build_params_dict`** in `core/params.py` to include the `distillationUnitSpecifications` key when provided.

### Example usage (target API)

```python
estimate_resources(
    algorithm_template="shor_2048",
    qubit_model="qubit_gate_ns_e3",
    distillation_units='[{"displayName": "15-1 RM", "numInputTs": 15, "numOutputTs": 1}]'
)
```

### References

- [Azure Quantum: Resource Estimator Target Parameters](https://learn.microsoft.com/en-us/azure/quantum/overview-resources-estimator)
- [Azure Quantum: Output Data](https://learn.microsoft.com/en-us/azure/quantum/overview-resource-estimator-output-data)
