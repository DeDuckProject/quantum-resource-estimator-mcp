"""Predefined algorithm templates with logical resource counts from published research."""

from __future__ import annotations

from dataclasses import dataclass


_TEMPLATE_DISCLAIMER = (
    "Templates are provided for demonstration and system exploration only. "
    "For research-grade estimates, provide your own logical_counts sourced directly "
    "from primary publications."
)


@dataclass(frozen=True)
class AlgorithmTemplate:
    id: str
    name: str
    description: str
    category: str
    logical_counts: dict[str, int]
    parameters: dict[str, str]
    source: str
    notes: str = ""
    caveats: tuple[str, ...] = ()


ALGORITHM_TEMPLATES: dict[str, AlgorithmTemplate] = {
    "shor_2048": AlgorithmTemplate(
        id="shor_2048",
        name="Shor's Algorithm (RSA-2048)",
        description=(
            "Shor's integer factoring algorithm applied to a 2048-bit RSA modulus. "
            "Breaking RSA-2048 encryption requires factoring a 2048-bit semiprime. "
            "This is the most commonly cited cryptographic threat from quantum computing."
        ),
        category="cryptography",
        logical_counts={
            "numQubits": 6189,
            "tCount": 0,
            "rotationCount": 0,
            "rotationDepth": 0,
            "cczCount": 2624225018,
            "ccixCount": 0,
            "measurementCount": 0,
        },
        parameters={
            "rsa_modulus_bits": "2048 (fixed for this template)",
        },
        source="Gidney & Ekerå, Quantum 5, 433 (2021). arXiv:1905.09749",
        notes=(
            "Logical counts derived from paper formulas at n=2048: "
            "numQubits = 3n + 0.002n·lg(n), cczCount = 0.3n³ + 0.0005n³·lg(n). "
            "Uses windowed arithmetic; no arbitrary rotations. "
            "The paper also reports a measurement depth of ~2.14 billion (not a gate count)."
        ),
        caveats=(
            _TEMPLATE_DISCLAIMER,
            "Counts are derived from the paper's closed-form formulas at n=2048, "
            "not from an explicit circuit compilation.",
            "measurementCount=0: the paper reports measurement depth (~2.14 billion), "
            "not a total measurement gate count.",
        ),
    ),
    "grover_aes128": AlgorithmTemplate(
        id="grover_aes128",
        name="Grover's Search (AES-128 Key Recovery)",
        description=(
            "Grover's algorithm applied to AES-128 key search, providing a quadratic "
            "quantum speedup. Effectively halves the security level from 128 to 64 bits. "
            "Requires a quantum oracle implementing AES-128 encryption."
        ),
        category="cryptography",
        logical_counts={
            "numQubits": 1665,
            "tCount": 54908,
            "rotationCount": 0,
            "rotationDepth": 0,
            "cczCount": 13727,
            "ccixCount": 0,
            "measurementCount": 13727,
        },
        parameters={
            "key_size_bits": "128 (fixed for this template)",
            "iterations": "~2^63 Grover iterations needed for full key search",
        },
        source=(
            "Jaques, Naehrig, Roetteler, Virdia. EUROCRYPT 2020. "
            "Implementing Grover oracles for quantum key search on AES and LowMC. "
            "arXiv:1910.01700"
        ),
        notes=(
            "Counts are per single oracle call (in-place MixColumn, r=1 configuration, "
            "Table 8 of the paper). Uses AND gates (Toffoli with |0⟩ target): each AND "
            "gate costs 4 T gates and 1 measurement. cczCount = AND gate count = measurementCount. "
            "Full Grover key search requires ~2^63 oracle iterations; these counts represent "
            "the circuit cost per iteration."
        ),
        caveats=(
            _TEMPLATE_DISCLAIMER,
            "WARNING: These counts represent a SINGLE oracle call (one Grover iteration), "
            "not the full key search. Full AES-128 key recovery requires ~2^63 oracle "
            "iterations. The estimate shown reflects per-iteration resources only and "
            "dramatically underestimates total resources for a complete attack.",
        ),
    ),
    "chemistry_femo": AlgorithmTemplate(
        id="chemistry_femo",
        name="FeMo-cofactor Simulation (Quantum Chemistry)",
        description=(
            "Quantum phase estimation to simulate the FeMo-cofactor, the active site "
            "of nitrogenase enzyme responsible for biological nitrogen fixation. "
            "A landmark application of quantum computing to chemistry and drug discovery. "
            "Uses tensor hypercontraction (THC) with the Reiher et al. Hamiltonian "
            "(108 spin orbitals)."
        ),
        category="chemistry",
        logical_counts={
            "numQubits": 2142,
            "tCount": 0,
            "rotationCount": 0,
            "rotationDepth": 0,
            "cczCount": 5300000000,
            "ccixCount": 0,
            "measurementCount": 0,
        },
        parameters={
            "active_space": "108 spin orbitals (Reiher et al. Hamiltonian)",
            "precision": "Chemical accuracy (~1 mHartree)",
            "thc_rank": "M=350 (recommended operating point)",
        },
        source=(
            "Lee et al., PRX Quantum 2, 030305 (2021). "
            "Even More Efficient Quantum Computations of Chemistry Through Tensor Hypercontraction. "
            "arXiv:2011.03494"
        ),
        notes=(
            "Numbers from Table III / Table IV (THC algorithm, Reiher Hamiltonian, M=350). "
            "The paper does not report T gates or rotations separately — costed entirely in Toffolis. "
            "The Li et al. Hamiltonian (152 spin orbitals) is more physically accurate but less "
            "commonly cited: 2,196 qubits, 3.2×10^10 Toffolis."
        ),
        caveats=(
            _TEMPLATE_DISCLAIMER,
            "rotationCount=0 is correct: the THC algorithm compiles all rotations into "
            "Toffoli gates as part of the paper's resource analysis. The cczCount already "
            "accounts for this.",
            "Based on the Reiher et al. Hamiltonian (108 spin orbitals).",
        ),
    ),
    "qpe_generic": AlgorithmTemplate(
        id="qpe_generic",
        name="Quantum Phase Estimation (Generic)",
        description=(
            "Generic quantum phase estimation (QPE) circuit for estimating eigenvalues "
            "of a unitary operator. A fundamental building block used in chemistry "
            "simulation, optimization, and quantum ML. Parameterized by problem size."
        ),
        category="general",
        logical_counts={
            "numQubits": 100,
            "tCount": 203,
            "rotationCount": 112,
            "rotationDepth": 100,
            "cczCount": 0,
            "ccixCount": 0,
            "measurementCount": 0,
        },
        parameters={
            "num_qubits": "Configurable — this template uses 100 logical qubits",
            "precision_bits": "Configurable — determines T-count",
        },
        source="Standard quantum algorithm; see Nielsen & Chuang, Chapter 5.",
        notes=(
            "This is a placeholder with representative counts for a 100-qubit QPE. "
            "For accurate estimates, provide your own logical_counts matching your "
            "specific unitary and precision requirements."
        ),
        caveats=(
            _TEMPLATE_DISCLAIMER,
            "Placeholder template — counts are illustrative, not from a specific published "
            "algorithm instance. Do not use for research estimates.",
        ),
    ),
}

VALID_TEMPLATE_IDS = set(ALGORITHM_TEMPLATES.keys())

CATEGORY_DESCRIPTIONS = {
    "cryptography": "Quantum algorithms that threaten or analyze classical cryptographic schemes.",
    "chemistry": "Quantum simulation of molecular and material systems for drug discovery and materials science.",
    "general": "General-purpose quantum algorithms applicable across multiple domains.",
    "optimization": "Quantum algorithms for combinatorial and continuous optimization problems.",
}
