# Security and read-only design

The installed CLI contains no AWS SDK, network client, shell invocation, or apply/delete command. It reads two local JSON files and prints a report. It neither modifies these inputs nor contacts S3. Tests include evaluating the example with socket creation blocked.

No credentials are needed. Do not put AWS access keys, real customer inventories, private object names, or account-specific data in issues or commits. Reports contain object keys, version IDs, and rule IDs. Review reports before sharing them. Samples in this repository are entirely synthetic.

The CLI does not certify a bucket or policy as safe. Unsupported features are rejected, and competing candidates remain unresolved. It loads input in memory; use trusted, reasonably sized files. It does not provide resource isolation for hostile JSON.

For suspected security problems, avoid posting credentials or private data publicly. Contact the repository owner privately through an available GitHub profile contact method; if none exists, open a minimal issue requesting a private reporting channel without exploit details or sensitive data.
