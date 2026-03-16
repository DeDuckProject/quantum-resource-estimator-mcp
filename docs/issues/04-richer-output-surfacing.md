## Title
feat: surface T-factory internals and full output fields in formatted results

## Labels
`enhancement`, `dx` (developer experience)

## Body

### Summary

The MCP passes through the full raw qsharp result dict in the `details` key, but the `summary` only surfaces 7 top-level metrics. Microsoft's QRE produces ~50+ output fields across several groups. Several fields that are important for advanced analysis (T-factory round structure, distillation error rates, logical qubit details) are buried and undocumented in `details`.

### What Microsoft's QRE provides in full output

**`physicalCounts.breakdown`** — beyond what's surfaced:
- `physicalQubitsForAlgorithm`
- `physicalQubitsForTfactories`
- `requiredLogicalQubitErrorRate`
- `requiredLogicalTstateErrorRate`
- `numTstates`
- `cliffordErrorRate`

**`tfactory`** group — entirely unsurfaced in summary:
- `numRounds` — number of distillation rounds
- `numUnitsPerRound` — units per round (array)
- `unitNamePerRound` — distillation unit names per round
- `numInputTs` — total input T states
- `numOutputTs` — total output T states
- `logicalErrorRate` — T-state logical error rate achieved
- `physicalQubits` — qubits used by T factories
- `runtime` — T-factory runtime

**`logicalQubit`** group — partially surfaced (only `codeDistance`):
- `physicalQubits` — per logical qubit
- `logicalCycleTime` — actual cycle time used
- `logicalErrorRate` — achieved logical error rate
- `twoqubitGateErrorRate` — effective 2-qubit error rate

### What's currently missing

- `format_single_result()` in `core/result_formatter.py` only extracts 7 summary fields
- No structured sub-summary for T-factory details
- No documentation on what the `details` dict contains
- `format_frontier_results()` only extracts 5 fields per point (missing T-factory details)

### Proposed solution

1. **Extend `format_single_result()`** to include an explicit `t_factory_summary` dict with the key T-factory fields (rounds, units per round, input/output T counts, logical error rate achieved).
2. **Add a `logical_qubit_summary`** dict with cycle time, qubits-per-logical, and achieved logical error rate.
3. **Add a `physical_breakdown` dict** surfacing the algorithmic vs. T-factory qubit split.
4. **Document the `details` structure** in the tool docstring so LLMs and users know what keys to look for.
5. **Extend `format_frontier_results()`** to include T-factory copies and code distance per frontier point (already partially done but inconsistently).

### Why this matters

An LLM using this MCP cannot currently answer questions like "how many distillation rounds are needed?" or "what fraction of qubits are used by T factories?" without digging into an undocumented raw dict. Surfacing these fields explicitly makes the MCP much more useful for detailed analysis.
