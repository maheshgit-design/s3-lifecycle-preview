# Repository and releases

Canonical public repository: https://github.com/maheshgit-design/s3-lifecycle-preview

## Run from source

```sh
git clone https://github.com/maheshgit-design/s3-lifecycle-preview.git
cd s3-lifecycle-preview
python -m pip install .
python -m unittest discover -s tests -v
```

GitHub Actions runs the test matrix on pushes and pull requests. Review the Actions tab for the latest commit's results. There is no PyPI release or hosted web application for v0.1.

## Release checklist

Before publishing a future version, update the version and support matrix, run tests, verify the example report, and confirm hosted CI passes for the exact release commit. Review all samples and reports for private data before committing. Version tags and package publication are separate release steps.
