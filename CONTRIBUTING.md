# Contributing

Use Python 3.10+ and a virtual environment. Install with `python -m pip install .`, then run `python -m unittest discover -s tests -v`. For source edits without reinstalling, use `python -m pip install -e .`.

Changes to simulation semantics must include an AWS primary-source reference, boundary tests, and an update to docs/SUPPORT_MATRIX.md. Never silently ignore unsupported lifecycle fields. Keep the core evaluator pure and preserve the no-network runtime contract. Separate any future collector from the evaluator and test its API allowlist independently.

Tests cover UTC boundaries, leap days, version history, filter boundaries, tiny-object defaults, unsupported inputs, competing candidates, CLI errors, and deterministic example output. The example report is a fixture for regression detection; independent focused assertions verify the underlying behaviors.

A proposed improvement should explain the user problem, changed behavior, limitations, and validation. Do not commit real bucket data or credentials.
