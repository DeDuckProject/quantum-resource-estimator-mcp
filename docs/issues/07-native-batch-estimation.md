## Title
perf: use native qsharp batch estimation instead of sequential loop

## Labels
`performance`, `minor`

## Body

### Summary

`compare_configurations` and `run_batch_estimation` currently loop over parameter configurations and call `qsharp.estimate()` one at a time. The qsharp package supports native batch estimation by passing a **list** of parameter dicts in a single call, which may be more efficient.

### Current implementation

```python
# core/estimator.py — run_batch_estimation
def run_batch_estimation(..., params_list):
    results = []
    for params in params_list:
        result = run_estimation(..., params)  # sequential, one call per config
        results.append(result)
    return results
```

### What qsharp supports natively

```python
import qsharp

# Single call with a list of param dicts
result = qsharp.estimate(qsharp_code, params=[params_dict_1, params_dict_2, params_dict_3])
# Returns a list of results in one invocation
```

### Why this matters

- Avoids repeated qsharp interpreter startup overhead for each configuration
- For `compare_configurations(compare_all_models=True)` this means 6 configurations currently run as 6 separate calls; native batching does it in 1
- The current 60-second timeout applies per-call; native batching would need a single adjusted timeout for the whole batch

### Proposed solution

1. **Refactor `run_batch_estimation`** to call `qsharp.estimate(code, params=params_list)` in one shot for the Q# code path.
2. **For `LogicalCounts` path**: check whether `LogicalCounts.estimate()` also accepts a list — if so, do the same.
3. **Adjust timeout logic** for batch calls (total timeout = N × per-call timeout, or a separate batch timeout constant).
4. **Fall back to sequential loop** if the qsharp version doesn't support list params (add version check).

### Considerations

- This is a backend optimization; the MCP API surface does not change.
- Need to verify that the qsharp package version pinned in `pyproject.toml` supports list params in `estimate()`.
- The sequential fallback ensures backwards compatibility.
