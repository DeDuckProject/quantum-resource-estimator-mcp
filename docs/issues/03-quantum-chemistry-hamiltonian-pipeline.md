## Title
feat: quantum chemistry pipeline — FCIDUMP Hamiltonian input and built-in double-factorized algorithm

## Labels
`enhancement`, `feature-request`

## Body

### Summary

Microsoft's QRE has a dedicated quantum chemistry estimation path: it supports FCIDUMP Hamiltonian files and a built-in double-factorized qubitization algorithm. The MCP currently provides only one hardcoded chemistry template (`chemistry_femo`), which is insufficient for researchers who want to estimate resources for their own molecular systems.

### What Microsoft's QRE supports

- **FCIDUMP file input**: Users can supply a Hamiltonian in FCIDUMP format (a standard quantum chemistry file format output by tools like PySCF, ORCA, Molpro).
- **Built-in double-factorized qubitization**: The QRE bundles a state-of-the-art double-factorized qubitization algorithm and computes resource estimates directly from the Hamiltonian.
- **Default Hamiltonians**: Microsoft provides example Hamiltonians for common benchmark molecules (H₂, LiH, BeH₂, etc.) for quick experimentation.

### What's currently missing

- No `hamiltonian` input parameter (FCIDUMP path or content)
- No `chemistry_algorithm` selection parameter (e.g., double-factorized qubitization)
- Only one fixed chemistry template (`chemistry_femo`) — cannot estimate for arbitrary molecules
- `explain_parameters(use_case='chemistry')` gives generic guidance but cannot recommend molecule-specific parameters

### Proposed solution

1. **Add a `chemistry_estimate` tool** (or extend `estimate_resources`) that accepts:
   - `hamiltonian_fcidump`: path or inline content of an FCIDUMP file
   - `chemistry_algorithm`: string selector, e.g. `"double_factorized_qubitization"` (default)
   - Standard hardware/QEC/error-budget parameters
2. **Add more chemistry templates** to `algorithm_templates.py` for common benchmark molecules (H₂, LiH, FeMo-cofactor already exists, N₂, etc.) sourced from published literature.
3. **Update `explain_parameters(use_case='chemistry')`** to document the FCIDUMP pathway and molecule selection guidance.

### Considerations

- FCIDUMP support requires that the `qsharp` package version being used exposes this API — should add a version check and clear error message if not available.
- FCIDUMP files can be large; consider file path references rather than inline content for large systems.
- This is a significant scope expansion; a separate `chemistry_estimate` tool is cleaner than overloading `estimate_resources`.

### References

- [Azure Quantum: Chemistry Resource Estimation Tutorial](https://learn.microsoft.com/en-us/azure/quantum/tutorial-resource-estimator-chemistry)
- [Double-factorized qubitization algorithm — Lee et al., PRX Quantum 2021](https://journals.aps.org/prxquantum/abstract/10.1103/PRXQuantum.2.030305)
