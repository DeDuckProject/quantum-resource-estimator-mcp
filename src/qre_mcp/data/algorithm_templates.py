"""Predefined algorithm templates with logical resource counts from published research."""

from __future__ import annotations

from dataclasses import dataclass


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
            "numQubits": 4158,
            "tCount": 0,
            "rotationCount": 0,
            "rotationDepth": 0,
            "cczCount": 5765034507320,
            "ccixCount": 0,
            "measurementCount": 86975023396,
        },
        parameters={
            "rsa_modulus_bits": "2048 (fixed for this template)",
        },
        source="Babbush et al., npj Quantum Information 7, 90 (2021). arXiv:2110.13523",
        notes=(
            "Uses windowed arithmetic and lookup tables for efficient modular "
            "exponentiation. Represents state-of-the-art algorithm compilation."
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
            "numQubits": 3284,
            "tCount": 0,
            "rotationCount": 0,
            "rotationDepth": 0,
            "cczCount": 13657,
            "ccixCount": 0,
            "measurementCount": 0,
        },
        parameters={
            "key_size_bits": "128 (fixed for this template)",
            "iterations": "~2^63 Grover iterations needed",
        },
        source=(
            "Jaques et al., EUROCRYPT 2020. Quantum circuits for AES key search. "
            "arXiv:1904.07980"
        ),
        notes=(
            "The large number of CCZ gates comes from the AES S-box implementation. "
            "Total runtime is dominated by the number of Grover iterations needed."
        ),
    ),
    "chemistry_femo": AlgorithmTemplate(
        id="chemistry_femo",
        name="FeMo-cofactor Simulation (Quantum Chemistry)",
        description=(
            "Quantum phase estimation to simulate the FeMo-cofactor, the active site "
            "of nitrogenase enzyme responsible for biological nitrogen fixation. "
            "A landmark application of quantum computing to chemistry and drug discovery. "
            "Uses a double-factorized Hamiltonian representation with 54 spin orbitals."
        ),
        category="chemistry",
        logical_counts={
            "numQubits": 1592,
            "tCount": 0,
            "rotationCount": 501,
            "rotationDepth": 501,
            "cczCount": 720,
            "ccixCount": 0,
            "measurementCount": 0,
        },
        parameters={
            "active_space": "54 spin orbitals (76 electrons)",
            "precision": "Chemical accuracy (~1 mHartree)",
        },
        source=(
            "Lee et al., PRX Quantum 2, 030305 (2021). "
            "Even More Efficient Quantum Computations of Chemistry. arXiv:2011.03494"
        ),
        notes=(
            "Uses tensor hypercontraction for improved T-count efficiency. "
            "One of the most well-studied practical quantum chemistry problems."
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
    ),
}

VALID_TEMPLATE_IDS = set(ALGORITHM_TEMPLATES.keys())

CATEGORY_DESCRIPTIONS = {
    "cryptography": "Quantum algorithms that threaten or analyze classical cryptographic schemes.",
    "chemistry": "Quantum simulation of molecular and material systems for drug discovery and materials science.",
    "general": "General-purpose quantum algorithms applicable across multiple domains.",
    "optimization": "Quantum algorithms for combinatorial and continuous optimization problems.",
}
