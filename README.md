# s3-lifecycle-preview

**See which objects could become eligible for S3 lifecycle actions before changing a policy.**

A dependency-free, offline Python CLI. Supply an AWS-style lifecycle policy, a normalized object/version inventory, and an explicit evaluation time. Get a deterministic JSON or readable report with rule IDs, version IDs, eligibility dates, and competing action flags.

**v0.1 is a snapshot eligibility simulator.** It does not apply actions, forecast an evolving bucket, resolve action precedence, or calculate savings. Read the [support matrix](docs/SUPPORT_MATRIX.md) before using a report for decisions. Unsupported fields are errors, including in disabled rules.

## Quick start

Python 3.10 or newer. From this repository:

```sh
python -m venv .venv
# Linux/macOS:
. .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install .
s3-lifecycle-preview --policy examples/policy.json --inventory examples/inventory.json --as-of 2026-04-01T00:00:00Z --format text
```

No AWS account, credentials, runtime packages, or network access are required for evaluation. Installation may download the setuptools build dependency. For an entirely offline source run on Linux/macOS:

```sh
PYTHONPATH=src python -m s3_lifecycle_preview --policy examples/policy.json --inventory examples/inventory.json --as-of 2026-04-01T00:00:00Z
```

The sample models four versions/markers: an old version eligible for deletion, a current object eligible for archival, a tiny object excluded from the default transition size range, and a sole delete marker eligible for cleanup. It produces **5 candidate actions, 3 eligible now**. See [the complete expected report](examples/expected-report.json).

## Reports and automation

```sh
s3-lifecycle-preview --policy examples/policy.json --inventory examples/inventory.json --as-of 2026-04-01T00:00:00Z > report.json
s3-lifecycle-preview --policy examples/policy.json --inventory examples/inventory.json --as-of 2026-04-01T00:00:00Z --fail-on-eligible
```

| Exit code | Meaning |
| --- | --- |
| 0 | Valid report; default behavior even when actions are eligible |
| 1 | `--fail-on-eligible` supplied and at least one action is eligible |
| 2 | Invalid arguments, unreadable JSON, invalid inventory, or unsupported feature |

Errors go to stderr; failed evaluations produce no report on stdout. `--fail-on-eligible` includes transitions and marker creation, not only permanent deletion. Shell redirection writes a local report; the CLI itself only reads input files and prints output.

Each event is an independent **candidate**, not a promise of execution. `eligible` means the modeled threshold has been reached; `scheduled` means a future threshold assuming the snapshot stays unchanged. Multiple eligible candidates for the same version are reported under `competing_candidates` without choosing a winner. Future candidates can become invalid after earlier actions, uploads, or policy changes. Counts are action counts, not unique objects or estimated bytes saved.

## Inputs

- [Policy and inventory format](docs/INPUTS.md): required metadata and examples.
- [Explicit support matrix](docs/SUPPORT_MATRIX.md): supported behavior, rejected features, and assumptions.
- [Security and read-only design](SECURITY.md): no AWS SDK or apply command.
- [Development guide](CONTRIBUTING.md): tests and extension requirements.
- [Publication instructions](docs/PUBLISHING.md): repository and future release instructions.

## Test

```sh
python -m pip install .
python -m unittest discover -s tests -v
```

GitHub Actions is configured for Python 3.10–3.14 on Ubuntu and a Python 3.12 smoke/test job on Windows. These are configured CI targets, not a claim that hosted CI has run. Local verification details are in [VALIDATION.md](docs/VALIDATION.md).

## Why a limited simulator?

S3 lifecycle eligibility depends on more than object age. Version history, filter boundaries, small-object transition defaults, and competing rules can change the result. This first release favors explicit assumptions and rejected unsupported cases over silently treating an incomplete report as authoritative.

AWS executes lifecycle actions asynchronously; eligibility dates are not deletion deadlines. The project's scope is documented against [AWS lifecycle elements](https://docs.aws.amazon.com/AmazonS3/latest/userguide/intro-lifecycle-rules.html), [transition constraints](https://docs.aws.amazon.com/AmazonS3/latest/userguide/lifecycle-transition-general-considerations.html), and [expiration behavior](https://docs.aws.amazon.com/AmazonS3/latest/userguide/lifecycle-expire-general-considerations.html).

GNU GPLv3 licensed. Independent project; not affiliated with or endorsed by AWS.
