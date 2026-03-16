# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-03-16

### Added
- Initial release of the Quantum Resource Estimator MCP server
- 8 MCP tools: `estimate_resources`, `compare_configurations`, `generate_frontier`,
  `list_qubit_models`, `list_qec_schemes`, `list_algorithm_templates`,
  `explain_parameters`, `custom_qubit_model_estimate`
- 2 MCP prompts: `guided_estimation`, `architecture_comparison`
- 2 MCP resources: `qre://qubit-models`, `qre://algorithm-catalog`
- 6 predefined qubit models (gate-based ns/μs, Majorana)
- 2 QEC schemes: `surface_code`, `floquet_code`
- 4 algorithm templates from published research: `shor_2048`, `grover_aes128`,
  `chemistry_femo`, `qpe_generic`
- Support for custom qubit model parameters and QEC scheme overrides
- Pareto frontier (qubit count vs. runtime) generation
- File-based rotating log at `~/.local/share/qre-mcp/qre-mcp.log`
- 60-second timeout guard for resource estimation calls
- Domain-specific guidance for cryptography, chemistry, and optimization use cases
