# Contributing

Thank you for your interest in contributing to the Quantum Resource Estimator MCP server.

## Getting Started

1. Fork the repository and clone your fork.
2. Create a virtual environment and install dev dependencies:
   ```bash
   uv sync --extra dev
   ```
3. Create a branch for your change:
   ```bash
   git checkout -b my-feature
   ```

## Running Tests

Unit tests (no qsharp/.NET required):
```bash
uv run pytest tests/ -m "not integration" -v
```

Integration tests (requires qsharp and .NET runtime):
```bash
uv run pytest tests/ -m integration -v
```

## Code Style

- Follow existing code conventions (type hints, docstrings, error handling patterns).
- Keep changes focused — one feature or fix per pull request.
- Add or update tests for any behaviour you change.

## Submitting a Pull Request

1. Ensure all unit tests pass.
2. Write a clear PR description explaining the motivation and what changed.
3. Reference any related issues.

## Reporting Issues

Open an issue on GitHub with:
- A clear description of the problem or feature request.
- Steps to reproduce (for bugs).
- Expected vs. actual behaviour.
- Python version, OS, and package versions if relevant.
