class QREError(Exception):
    """Base exception for quantum resource estimator errors."""


class InvalidQubitModelError(QREError):
    """Raised when an unknown qubit model name is provided."""


class IncompatibleQECSchemeError(QREError):
    """Raised when a QEC scheme is incompatible with the selected qubit model.

    For example, floquet_code requires Majorana qubits.
    """


class InvalidErrorBudgetError(QREError):
    """Raised when error budget values are out of range or inconsistent."""


class AlgorithmInputError(QREError):
    """Raised when algorithm input is missing, ambiguous, or invalid."""


class EstimationFailedError(QREError):
    """Raised when the qsharp estimator returns an error."""


class NoFeasibleSolutionError(QREError):
    """Raised when no feasible solution exists under the given constraints."""


class UnknownAlgorithmTemplateError(QREError):
    """Raised when a named algorithm template does not exist."""


class InvalidQubitParamOverrideError(QREError):
    """Raised when qubit_model_overrides contains unknown parameter keys."""


class InvalidQECSchemeParamError(QREError):
    """Raised when custom QEC scheme parameters are out of range."""


class InvalidReactionTimeError(QREError):
    """Raised when the reaction_time parameter is invalid (bad format, zero, or negative)."""
