## Title
feat: document and expose estimation caching for large Q# programs

## Labels
`enhancement`, `documentation`

## Body

### Summary

Microsoft's QRE supports caching subroutine cost estimates in Q# programs via `BeginEstimateCaching` / `EndEstimateCaching`. For large circuits with repeated subroutines this can drastically reduce estimation time. The MCP neither documents nor provides tooling around this capability.

### What Microsoft's QRE supports

In Q# code, you can annotate repeated blocks so the estimator only counts them once:

```qsharp
operation MyCircuit() : Unit {
    for i in 0..999 {
        let cacheKey = BeginEstimateCaching("MySubroutine", i);
        if cacheKey {
            // expensive subroutine — only counted once
            MyExpensiveSubroutine();
            EndEstimateCaching();
        }
    }
}
```

Additionally, you can pass **pre-calculated logical counts** for subroutines you already know the cost of, combining them with Q# code for the rest of the circuit via `FactoringFromLogicalCounts`.

### What's currently missing

- No mention of `BeginEstimateCaching` / `EndEstimateCaching` in the MCP documentation, prompts, or `explain_parameters`
- No guidance on when to use caching vs. full estimation
- No example Q# code demonstrating caching in the algorithm templates or docs
- The 60-second timeout (`_ESTIMATION_TIMEOUT_S`) will silently cut off large programs that would benefit from caching — users are not told caching is an option

### Proposed solution

1. **Update `explain_parameters()`** to mention caching when `use_case` involves large or repeated subroutines.
2. **Add a caching guidance note** to the timeout error message in `core/estimator.py` — suggest `BeginEstimateCaching` as an alternative to relaxing constraints.
3. **Add an example Q# snippet** with caching to the `guided_estimation` prompt and/or the README.
4. **Consider a `qsharp_subroutine_costs` parameter** on `estimate_resources` that accepts a JSON dict of pre-calculated subroutine logical counts to inject via `FactoringFromLogicalCounts`.

### Example improved timeout error message

```
Resource estimation timed out after 60s.
Options:
  1. Relax constraints (max_duration, max_physical_qubits).
  2. Use BeginEstimateCaching/EndEstimateCaching in your Q# code to cache repeated subroutines.
  3. Pre-calculate subroutine costs and pass them via logical_counts.
```

### References

- [Azure Quantum: Caching documentation](https://learn.microsoft.com/en-us/azure/quantum/how-to-submit-re-jobs)
- `BeginEstimateCaching`, `EndEstimateCaching` operations in Q# standard library
