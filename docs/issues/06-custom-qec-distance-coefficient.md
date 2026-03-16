## Title
feat: expose `distanceCoefficientPower` for fully custom QEC schemes

## Labels
`enhancement`, `minor`

## Body

### Summary

Microsoft's QRE allows users to define fully custom QEC schemes by specifying `distanceCoefficientPower` alongside the other QEC parameters. The MCP exposes most QEC overrides but omits this field, preventing users from accurately modeling non-standard error correction codes.

### What Microsoft's QRE supports

A complete custom QEC scheme requires:
- `crossingPrefactor` ✅ (exposed via `qec_crossing_prefactor`)
- `errorCorrectionThreshold` ✅ (exposed via `qec_error_correction_threshold`)
- `logicalCycleTime` ✅ (exposed via `qec_logical_cycle_time`)
- `physicalQubitsPerLogicalQubit` ✅ (exposed via `qec_physical_qubits_per_logical`)
- `distanceCoefficientPower` ❌ **not exposed** — controls how code distance scales in the error suppression formula

### What `distanceCoefficientPower` does

The logical error rate formula used by the QRE is:

```
logical_error_rate = crossingPrefactor * (physical_error_rate / errorCorrectionThreshold)^((codeDistance + 1) / distanceCoefficientPower)
```

The default value (for surface code) is `2`. For codes with different distance scaling (e.g., color codes, concatenated codes), this parameter must be adjustable to get accurate estimates.

### What's currently missing

- `distanceCoefficientPower` not in `build_params_dict()` signature in `core/params.py`
- Not accepted by `estimate_resources`, `generate_frontier`, or `compare_configurations`
- Not documented in `list_qec_schemes()` output

### Proposed solution

1. **Add `qec_distance_coefficient_power` parameter** (float) to `build_params_dict()` in `core/params.py`.
2. **Expose it** in `estimate_resources`, `generate_frontier`, and `compare_configurations` tool signatures.
3. **Add to validation** in `core/validators.py` (must be a positive float).
4. **Document in `list_qec_schemes()`** that custom schemes can set this value and what the default is.

### Effort estimate

Small — this is a one-line addition to `build_params_dict` and corresponding parameter threading through the tool signatures. The main work is documentation and validation.
