# Support matrix — v0.1.0

This is a **complete statement of the intended supported subset**, not an AWS conformance certification. The simulator evaluates independent candidates against one complete snapshot. It never advances object state. Unknown input fields fail validation; unsupported configuration is not silently ignored.

| Area | Status | Exact behavior / limitation |
| --- | --- | --- |
| Offline Python CLI | Supported | JSON files in, JSON/text on stdout; no AWS client, network, or credentials |
| Runtime | Supported design | Python >=3.10, standard library only; see VALIDATION.md for executed environments |
| General-purpose S3 buckets | Supported subset | Versioning `Enabled` or `Disabled`; user supplies normalized complete inventory |
| Suspended versioning / directory buckets | Unsupported | Suspended is rejected; directory buckets are outside the input model |
| Policy shape | Supported subset | JSON `Rules` list; AWS SDK/CLI field names, not XML, Terraform, or CloudFormation |
| Disabled rules | Supported | Validated but not evaluated |
| Prefix | Supported | Case-sensitive starts-with match; legacy `Prefix` or `Filter.Prefix` |
| Tags | Supported | Exact string key/value equality; Tag and And.Tags |
| Size filter | Supported | Strict greater-than / less-than byte boundaries; equality is excluded |
| And | Supported | Prefix, multiple tags, size conditions; at least two predicates |
| Current expiration | Supported | Positive Days or midnight UTC Date; unversioned permanent-delete candidate, enabled-versioning marker-create candidate |
| Noncurrent expiration | Supported subset | Positive NoncurrentDays, measured from successor creation via noncurrent_since |
| NewerNoncurrentVersions | Rejected | Retain-N history-dependent behavior is not implemented for either action |
| ExpiredObjectDeleteMarker | Supported subset | Sole remaining current marker, prefix-only filter; no cleanup while other versions remain |
| Age-based marker cleanup | Supported subset | Sole current marker only; size filters do not produce cleanup candidates |
| Noncurrent delete markers | Not simulated | No direct deletion or transition candidate; still included when deciding whether a marker is sole |
| Marker cleanup timestamp | Observation only | `eligible_at` is no earlier than as-of; the snapshot does not reveal when other versions were removed |
| Transitions | Supported subset | STANDARD source to STANDARD_IA, GLACIER (Flexible Retrieval), or DEEP_ARCHIVE |
| Noncurrent transitions | Supported subset | Same targets; positive NoncurrentDays based on supplied successor timestamp |
| STANDARD_IA restrictions | Supported subset | Days/NoncurrentDays >=30; absolute Date transitions rejected |
| Transition default size | Fixed modern default | Objects <131072 bytes excluded unless rule has explicit size filter; exact 131072 included |
| Legacy small-object transition default | Not modeled | Configurations with varies_by_storage_class behavior must not be evaluated under this model |
| Other source/target classes | Rejected | No Intelligent-Tiering, Glacier Instant Retrieval, One Zone-IA, RRS, or chained transition state |
| Days and UTC | Supported | Add days, then move to following midnight UTC; offsets normalized; timezone-less input rejected |
| Absolute Date | Supported subset | Expiration and GLACIER/DEEP_ARCHIVE current transitions; dates must be midnight UTC; candidate cannot precede object creation |
| Overlapping rules | Candidates only | All matched action candidates retained; multiple currently eligible actions per version flagged |
| Conflict precedence | Not resolved | Do not infer execution order from event sorting or count every candidate as an actual action |
| Full temporal simulation | Not implemented | No marker creation in state, no future noncurrent history, no successive transitions or cleanup cascades |
| Object Lock / replication | Rejected | Metadata must explicitly declare both false; protected and replication-dependent behavior not predicted |
| AbortIncompleteMultipartUpload | Rejected | Upload inventory/action model absent |
| Partial/sample bucket inventories | Rejected declaration | complete must be true; tool cannot independently verify completeness |
| Version timestamps | Validated subset | Each key has one latest version; unique timestamps; noncurrent_since equals successor last_modified |
| AWS Inventory CSV / Parquet import | Not implemented | Requires conversion to documented JSON; no claim of native AWS Inventory support |
| Live AWS reads / policy writes | Not implemented | No AWS API operations of any kind |
| Billing, minimum-duration charges, savings | Not implemented | size_bytes is source metadata, not avoided billing or freed storage |
| AWS server-side validation | Not implemented | Local subset validation does not prove AWS will accept a proposed policy |
| Execution timing / propagation | Not predicted | Actual AWS action completion is asynchronous |
| Huge inventories | In-memory only | No streaming; version sorting and report memory scale with input and matched rules |

## Interpreting conflict flags

AWS documents permanent deletion before transition, transition before delete-marker creation, and preferences among some competing transitions. v0.1 deliberately reports candidates without applying that precedence. For example, `create_delete_marker` and `transition` being eligible does **not** mean both execute today. A future event can also be prevented by an earlier action. No chronological forecast is implied.

## Inputs are assertions

`complete: true`, `object_lock: false`, and `replication: false` are user assertions. The program cannot verify a real bucket's state. Only use this version with complete histories for the keys represented, and only when the declared bucket-wide assumptions hold. For bucket-wide totals, every key/version/marker must be included. The synthetic example is a complete fictional bucket, not a sample declared complete for a real bucket.

## Sources

Behavior reviewed on 2026-09-07 against:

- [Lifecycle configuration elements](https://docs.aws.amazon.com/AmazonS3/latest/userguide/intro-lifecycle-rules.html)
- [Transition constraints and minimum object sizes](https://docs.aws.amazon.com/AmazonS3/latest/userguide/lifecycle-transition-general-considerations.html)
- [Expiration and precedence](https://docs.aws.amazon.com/AmazonS3/latest/userguide/lifecycle-expire-general-considerations.html)
- [Lifecycle timing troubleshooting](https://docs.aws.amazon.com/AmazonS3/latest/userguide/troubleshoot-lifecycle.html)

These references explain AWS behavior; the table above defines the narrower implementation contract.
