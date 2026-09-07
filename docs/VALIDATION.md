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
| GitHub hosted CI | All six jobs passed for implementation commit ba35c170d249f8d82b58f2bf05eef285a7148c74 |
| AWS integration/conformance | Not performed; tool intentionally has no AWS API integration |

Commands executed from the source parent:

```sh
python -m pip install --no-index --no-build-isolation --no-deps ./s3-lifecycle-preview
python -m unittest discover -s s3-lifecycle-preview/tests -v
```

The installed console script was also executed with the documented example inputs and text format. The test suite checks a JSON fixture and independent boundary expectations. Hosted verification passed on Ubuntu with Python 3.10–3.14 and Windows with Python 3.12. Each job installed the package, ran the 26 tests, and executed the console example. [Verified run](https://github.com/maheshgit-design/s3-lifecycle-preview/actions/runs/34147365103).
