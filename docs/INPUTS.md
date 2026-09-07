# Input contract

Read the [support matrix](SUPPORT_MATRIX.md) first. Both inputs are UTF-8 JSON. Duplicate JSON keys, unknown fields, and unsupported actions fail with exit code 2. Do not include AWS response wrappers such as ResponseMetadata in policy JSON.

## Lifecycle policy

```json
{
  "Rules": [
    {
      "ID": "expire-logs",
      "Status": "Enabled",
      "Filter": {"Prefix": "logs/"},
      "Expiration": {"Days": 60}
    }
  ]
}
```

`Rules` must contain 1–1000 entries. IDs, when present, must be unique nonempty strings up to 255 characters. Absent IDs become `rule-1`, `rule-2`, etc.; explicit IDs cannot collide with these generated IDs. Every rule requires Status, Filter (use `{}` for all objects) or legacy Prefix, and at least one action. Supported actions and filters are enumerated in the support matrix.

## Inventory

```json
{
  "schema_version": 1,
  "versioning": "Disabled",
  "complete": true,
  "object_lock": false,
  "replication": false,
  "objects": [
    {
      "key": "logs/app.json",
      "version_id": "null",
      "is_latest": true,
      "delete_marker": false,
      "last_modified": "2026-01-01T12:00:00Z",
      "size": 262144,
      "storage_class": "STANDARD",
      "tags": {}
    }
  ]
}
```

| Field | Contract |
| --- | --- |
| schema_version | Integer 1 |
| versioning | Enabled or Disabled (Disabled means never-versioned) |
| complete | Boolean true, declaring complete supplied histories |
| object_lock / replication | Boolean false; any enabled configuration is outside v0.1 |
| objects | List; empty list valid for an empty bucket |
| key / version_id | Nonempty strings; `(key, version_id)` must be unique |
| is_latest / delete_marker | Required JSON booleans |
| last_modified | ISO-8601 timestamp with timezone, no later than as-of |
| noncurrent_since | Required only for noncurrent versions; equals immediate successor's last_modified |
| size | Nonnegative integer bytes, not a string or boolean |
| storage_class | STANDARD only, also used as a placeholder for markers |
| tags | Required string-to-string map; empty map only when there are no tags |

A never-versioned object may use string `"null"` as version_id. Each key needs exactly one latest version. Never-versioned inventories cannot contain historical versions or markers. Delete markers use size 0 and tags `{}`. Noncurrent versions retain their own tags.

Do not estimate noncurrent_since from the old version's last_modified: a version can remain current for years. Use the timestamp of its immediate successor, which may itself be a delete marker. Equal version timestamps are rejected because chronological ordering is ambiguous in this input model.

## Collecting data

This release has no live collection command. Prepare a normalized JSON export using an independently reviewed, read-only collection process. Raw `list-objects-v2`, `list-object-versions`, and AWS Inventory outputs are not accepted directly: they lack this exact schema and may omit required tags/history/context. Pagination and completeness must be handled by your collector. Never mark a partial listing complete to bypass validation.

## Output

JSON has schema_version, mode, as_of, assumptions, summary, competing_candidates, and events. Events include key, version_id, rule_id, action, eligible_at, status, size_bytes, reason, and optional target_storage_class. The CLI sorts events deterministically by key, version, date, rule and action. This ordering is for readability, not execution precedence.

An empty events array means no candidates were produced under supported assumptions; it is not a general certification of bucket safety. Unmatched rules, default-size exclusions, and noncurrent delete markers do not produce events.
