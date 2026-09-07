"""Pure snapshot evaluator; never applies actions or invents future version history."""
from collections import Counter
from datetime import datetime, timedelta, timezone

UTC = timezone.utc
TARGETS = {"STANDARD_IA", "GLACIER", "DEEP_ARCHIVE"}


class PreviewError(ValueError):
    """Invalid input or a feature outside the documented support matrix."""


def require(condition, message):
    if not condition:
        raise PreviewError(message)


def mapping(value, where, allowed, required=()):
    require(isinstance(value, dict), f"{where}: expected an object")
    require(not (set(value) - set(allowed)),
            f"{where}: unsupported fields {sorted(set(value) - set(allowed))}")
    require(set(required) <= set(value), f"{where}: required fields {sorted(required)}")


def integer(value, where, minimum=0):
    require(type(value) is int and value >= minimum, f"{where}: integer >= {minimum} required")


def timestamp(value):
    require(isinstance(value, str), "timestamp must be an ISO-8601 string with timezone")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise PreviewError(f"invalid timestamp: {value}") from exc
    require(result.tzinfo is not None, "timestamp must include a timezone")
    return result.astimezone(UTC)


def iso(value):
    return value.isoformat().replace("+00:00", "Z")


def age_date(start, days):
    # AWS age-based actions round the result up to the following midnight UTC.
    try:
        date = timestamp(start) + timedelta(days=days)
        return (date + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    except OverflowError as exc:
        raise PreviewError("lifecycle date exceeds supported datetime range") from exc


def validate_filter(filt, where="Filter", nested=False):
    allowed = {"Prefix", "Tag", "ObjectSizeGreaterThan", "ObjectSizeLessThan"}
    if nested:
        allowed = (allowed - {"Tag"}) | {"Tags"}
    else:
        allowed |= {"And"}
    mapping(filt, where, allowed)
    if not nested:
        require(len(filt) <= 1, f"{where}: combine predicates with And")
    if "And" in filt:
        validate_filter(filt["And"], "Filter.And", True)
        terms = len(filt["And"]) + len(filt["And"].get("Tags", [])) - ("Tags" in filt["And"])
        require(terms >= 2, "Filter.And needs at least two predicates")
    if "Prefix" in filt:
        require(isinstance(filt["Prefix"], str), "Prefix must be a string")
    for key in ("ObjectSizeGreaterThan", "ObjectSizeLessThan"):
        if key in filt:
            integer(filt[key], key)
    if "ObjectSizeGreaterThan" in filt and "ObjectSizeLessThan" in filt:
        require(filt["ObjectSizeGreaterThan"] < filt["ObjectSizeLessThan"], "invalid size range")
    tags = [filt["Tag"]] if "Tag" in filt else filt.get("Tags", [])
    require(isinstance(tags, list), "Tags must be a list")
    keys = set()
    for tag in tags:
        mapping(tag, "Tag", {"Key", "Value"}, {"Key", "Value"})
        require(isinstance(tag["Key"], str) and bool(tag["Key"]) and isinstance(tag["Value"], str),
                "Tag Key must be nonempty and Value must be a string")
        require(tag["Key"] not in keys, "duplicate tag key")
        keys.add(tag["Key"])


def flat_filter(rule):
    filt = rule.get("Filter", {"Prefix": rule.get("Prefix", "")})
    return filt.get("And", filt)


def matches(filt, obj):
    if not obj["key"].startswith(filt.get("Prefix", "")):
        return False
    if "ObjectSizeGreaterThan" in filt and obj["size"] <= filt["ObjectSizeGreaterThan"]:
        return False
    if "ObjectSizeLessThan" in filt and obj["size"] >= filt["ObjectSizeLessThan"]:
        return False
    tags = [filt["Tag"]] if "Tag" in filt else filt.get("Tags", [])
    if tags and obj["delete_marker"]:
        return False
    return all(obj["tags"].get(t["Key"]) == t["Value"] for t in tags)


def timing(action, where, noncurrent=False):
    if noncurrent:
        require("NoncurrentDays" in action, f"{where}: NoncurrentDays required")
        integer(action["NoncurrentDays"], where, 1)
    else:
        require(("Days" in action) != ("Date" in action), f"{where}: specify exactly one of Days or Date")
        if "Days" in action:
            integer(action["Days"], where, 0 if "Transition" in where else 1)
        else:
            dt = timestamp(action["Date"])
            require(dt.hour == dt.minute == dt.second == dt.microsecond == 0, "Date must be midnight UTC")


def validate_policy(policy):
    mapping(policy, "policy", {"Rules"}, {"Rules"})
    require(isinstance(policy["Rules"], list) and 1 <= len(policy["Rules"]) <= 1000,
            "Rules must contain 1 to 1000 rules")
    ids = set()
    for index, rule in enumerate(policy["Rules"]):
        mapping(rule, f"rule {index}", {"ID", "Status", "Prefix", "Filter", "Expiration", "Transitions",
                "NoncurrentVersionExpiration", "NoncurrentVersionTransitions"}, {"Status"})
        require(rule["Status"] in ("Enabled", "Disabled"), "Status must be Enabled or Disabled")
        rid = rule.get("ID", f"rule-{index + 1}")
        require(isinstance(rid, str) and 0 < len(rid) <= 255 and rid not in ids, "rule IDs must be unique nonempty strings")
        ids.add(rid)
        require(not ("Prefix" in rule and "Filter" in rule), "Prefix and Filter are mutually exclusive")
        require("Prefix" in rule or "Filter" in rule, "rule must specify Prefix or Filter (use {} for all objects)")
        validate_filter(rule.get("Filter", {"Prefix": rule.get("Prefix", "")}))
        filt = flat_filter(rule)
        require(any(k in rule for k in ("Expiration", "Transitions", "NoncurrentVersionExpiration",
                                       "NoncurrentVersionTransitions")), "rule needs an action")
        if "Expiration" in rule:
            action = rule["Expiration"]
            mapping(action, "Expiration", {"Days", "Date", "ExpiredObjectDeleteMarker"})
            if "ExpiredObjectDeleteMarker" in action:
                require(len(action) == 1 and action["ExpiredObjectDeleteMarker"] is True, "delete-marker expiration must be true and standalone")
                require(not ({"Tag", "Tags", "ObjectSizeGreaterThan", "ObjectSizeLessThan"} & set(filt)),
                        "delete-marker cleanup supports prefix-only filters")
            else:
                timing(action, "Expiration")
        if "NoncurrentVersionExpiration" in rule:
            action = rule["NoncurrentVersionExpiration"]
            mapping(action, "NoncurrentVersionExpiration", {"NoncurrentDays"}, {"NoncurrentDays"})
            timing(action, "NoncurrentVersionExpiration", True)
        for key in ("Transitions", "NoncurrentVersionTransitions"):
            if key not in rule:
                continue
            require(isinstance(rule[key], list) and bool(rule[key]), f"{key} must be a nonempty list")
            noncurrent = key.startswith("Noncurrent")
            for action in rule[key]:
                mapping(action, key, {"StorageClass", "NoncurrentDays"} if noncurrent else {"StorageClass", "Days", "Date"}, {"StorageClass"})
                require(isinstance(action["StorageClass"], str) and action["StorageClass"] in TARGETS, f"{key}: supported targets are {sorted(TARGETS)}")
                timing(action, key, noncurrent)
                if action["StorageClass"] == "STANDARD_IA":
                    require("Date" not in action, "STANDARD_IA Date transitions are unsupported")
                    require(action.get("NoncurrentDays", action.get("Days", 0)) >= 30,
                            "STANDARD_IA transitions need at least 30 days")


def validate_inventory(data, as_of):
    mapping(data, "inventory", {"schema_version", "versioning", "complete", "object_lock", "replication", "objects"},
            {"schema_version", "versioning", "complete", "object_lock", "replication", "objects"})
    require(type(data["schema_version"]) is int and data["schema_version"] == 1, "schema_version must be 1")
    require(data["versioning"] in ("Enabled", "Disabled"), "Suspended versioning is unsupported")
    require(data["complete"] is True, "complete inventory required; samples cannot represent partial bucket listings")
    require(data["object_lock"] is False and data["replication"] is False,
            "Object Lock and replication configurations are unsupported")
    require(isinstance(data["objects"], list), "objects must be a list")
    groups = {}
    identities = set()
    for obj in data["objects"]:
        fields = {"key", "version_id", "is_latest", "delete_marker", "last_modified", "noncurrent_since", "size", "storage_class", "tags"}
        mapping(obj, "object", fields, fields - {"noncurrent_since"})
        require(isinstance(obj["key"], str) and bool(obj["key"]), "key must be a nonempty string")
        require(isinstance(obj["version_id"], str) and bool(obj["version_id"]), "version_id must be a nonempty string")
        require(type(obj["is_latest"]) is bool and type(obj["delete_marker"]) is bool, "version flags must be booleans")
        integer(obj["size"], "size")
        require(obj["storage_class"] == "STANDARD", "v0.1 supports only STANDARD source objects")
        require(isinstance(obj["tags"], dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in obj["tags"].items()), "tags must map strings to strings")
        modified = timestamp(obj["last_modified"])
        require(modified <= as_of, "object timestamp is after as-of")
        if not obj["is_latest"]:
            require("noncurrent_since" in obj, "noncurrent versions require noncurrent_since")
            require(modified <= timestamp(obj["noncurrent_since"]) <= as_of, "invalid noncurrent_since")
        else:
            require("noncurrent_since" not in obj, "latest version cannot have noncurrent_since")
        if obj["delete_marker"]:
            require(obj["size"] == 0 and obj["tags"] == {}, "delete marker must have zero size and no tags")
        identity = (obj["key"], obj["version_id"])
        require(identity not in identities, "duplicate object version")
        identities.add(identity)
        groups.setdefault(obj["key"], []).append(obj)
    for versions in groups.values():
        require(sum(o["is_latest"] for o in versions) == 1, "each key needs exactly one latest version")
        if data["versioning"] == "Disabled":
            require(len(versions) == 1 and not versions[0]["delete_marker"], "unversioned inventory cannot have historical versions or markers")
        # Complete histories must have unambiguous successor timestamps.
        ordered = sorted(versions, key=lambda o: timestamp(o["last_modified"]), reverse=True)
        require(ordered[0]["is_latest"], "latest version must have newest last_modified")
        for newer, older in zip(ordered, ordered[1:]):
            require(timestamp(newer["last_modified"]) > timestamp(older["last_modified"]), "equal version timestamps are unsupported")
            require(timestamp(older["noncurrent_since"]) == timestamp(newer["last_modified"]), "noncurrent_since must equal successor last_modified")
    return groups


def simulate(policy, inventory, as_of):
    """Return independent eligibility candidates for the supplied snapshot and instant.

    Does not mutate inputs, resolve competing transitions, or advance bucket state.
    """
    now = timestamp(as_of)
    validate_policy(policy)
    groups = validate_inventory(inventory, now)
    events = []
    for obj in inventory["objects"]:
        for index, rule in enumerate(policy["Rules"]):
            if rule["Status"] != "Enabled" or not matches(flat_filter(rule), obj):
                continue
            rid = rule.get("ID", f"rule-{index + 1}")

            def emit(action, due, target=None, reason="age threshold"):
                event = {"key": obj["key"], "version_id": obj["version_id"], "rule_id": rid,
                         "action": action, "eligible_at": iso(due), "status": "eligible" if due <= now else "scheduled",
                         "size_bytes": obj["size"], "reason": reason}
                if target:
                    event["target_storage_class"] = target
                events.append(event)

            def due_for(action, noncurrent=False):
                if "Date" in action:
                    return max(timestamp(action["Date"]), timestamp(obj["last_modified"]))
                return age_date(obj["noncurrent_since"] if noncurrent else obj["last_modified"],
                                action["NoncurrentDays"] if noncurrent else action["Days"])

            if obj["delete_marker"]:
                expiration = rule.get("Expiration", {})
                size_filter = {"ObjectSizeGreaterThan", "ObjectSizeLessThan"} & set(flat_filter(rule))
                if obj["is_latest"] and len(groups[obj["key"]]) == 1 and expiration and not size_filter:
                    due = now if "ExpiredObjectDeleteMarker" in expiration else max(now, due_for(expiration))
                    emit("remove_delete_marker", due, reason="sole marker observed at as-of; original cleanup eligibility time is unknown")
                continue
            if obj["is_latest"]:
                expiration = rule.get("Expiration", {})
                if expiration and "ExpiredObjectDeleteMarker" not in expiration:
                    emit("create_delete_marker" if inventory["versioning"] == "Enabled" else "expire_object", due_for(expiration))
                transitions = rule.get("Transitions", [])
            else:
                if "NoncurrentVersionExpiration" in rule:
                    emit("expire_noncurrent_version", due_for(rule["NoncurrentVersionExpiration"], True))
                transitions = rule.get("NoncurrentVersionTransitions", [])
            for transition in transitions:
                filt = flat_filter(rule)
                custom_size = bool({"ObjectSizeGreaterThan", "ObjectSizeLessThan"} & set(filt))
                if obj["size"] < 131072 and not custom_size:
                    continue
                emit("transition", due_for(transition, not obj["is_latest"]), transition["StorageClass"])
    events.sort(key=lambda e: (e["key"], e["version_id"], e["eligible_at"], e["rule_id"], e["action"], e.get("target_storage_class", "")))
    candidates = Counter((e["key"], e["version_id"]) for e in events if e["status"] == "eligible")
    conflicts = [{"key": k, "version_id": v, "candidate_count": count}
                 for (k, v), count in sorted(candidates.items()) if count > 1]
    return {"schema_version": 1, "mode": "snapshot-eligibility", "as_of": iso(now),
            "assumptions": ["No state changes are applied", "Scheduled candidates depend on unchanged snapshot metadata",
                            "Modern 128 KiB transition default; explicit size filters override", "Eligibility is not execution time"],
            "summary": {"objects_scanned": len(inventory["objects"]), "candidate_actions": len(events),
                        "eligible_actions": sum(e["status"] == "eligible" for e in events),
                        "objects_with_competing_candidates": len(conflicts)},
            "competing_candidates": conflicts, "events": events}
