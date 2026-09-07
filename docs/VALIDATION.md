# Validation record

Prepared 2026-09-07.

| Check | Result |
| --- | --- |
| Local environment | Linux, Python 3.12.13 |
| Wheel build and installation | Passed, using installed setuptools with no index or dependency downloads |
| Unit/integration tests | 26 tests passed, including parameterized cases |
| Installed console entry point | Passed with included example |
| Example output | 4 inventory records, 5 candidates, 3 currently eligible |
| Network-free evaluation | Example evaluation passed with socket creation blocked |
| Input immutability | Covered by test |
| GitHub hosted CI | Pending initial publication; consult GitHub Actions for the current commit |
| AWS integration/conformance | Not performed; tool intentionally has no AWS API integration |

Commands executed from the source parent:

```sh
python -m pip install --no-index --no-build-isolation --no-deps ./s3-lifecycle-preview
python -m unittest discover -s s3-lifecycle-preview/tests -v
```

The installed console script was also executed with the documented example inputs and text format. The test suite checks a JSON fixture and independent boundary expectations. Other Python/OS versions are configured in GitHub Actions but have not been locally verified.
