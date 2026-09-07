import copy
import unittest

from s3_lifecycle_preview.engine import PreviewError, age_date, simulate

AS_OF = "2026-04-01T00:00:00Z"


def obj(**changes):
    value = dict(key="logs/a", version_id="v1", is_latest=True, delete_marker=False,
                 last_modified="2026-01-01T12:00:00Z", size=200000, storage_class="STANDARD", tags={})
    value.update(changes)
    return value


def inventory(*objects, **changes):
    value = dict(schema_version=1, versioning="Disabled", complete=True,
                 object_lock=False, replication=False, objects=list(objects))
    value.update(changes)
    return value


def policy(**changes):
    rule = dict(ID="test", Status="Enabled", Filter={}, Expiration={"Days": 30})
    rule.update(changes)
    return {"Rules": [rule]}


class SimulationTests(unittest.TestCase):
    def run_preview(self, p=None, i=None, now=AS_OF):
        return simulate(p or policy(), i or inventory(obj()), now)

    def test_utc_rounding_and_boundary(self):
        p = policy(Expiration={"Days": 1})
        before = self.run_preview(p, now="2026-01-02T23:59:59Z")
        after = self.run_preview(p, now="2026-01-03T00:00:00Z")
        self.assertEqual(before["events"][0]["status"], "scheduled")
        self.assertEqual(after["events"][0]["status"], "eligible")
        self.assertEqual(after["events"][0]["eligible_at"], "2026-01-03T00:00:00Z")

    def test_offset_and_leap_day(self):
        self.assertEqual(age_date("2024-02-28T23:00:00-02:00", 1).isoformat(), "2024-03-02T00:00:00+00:00")

    def test_midnight_input(self):
        self.assertEqual(age_date("2026-01-01T00:00:00Z", 1).isoformat(), "2026-01-03T00:00:00+00:00")

    def test_unversioned_expiration(self):
        self.assertEqual(self.run_preview()["events"][0]["action"], "expire_object")

    def test_versioned_expiration(self):
        result = self.run_preview(i=inventory(obj(), versioning="Enabled"))
        self.assertEqual(result["events"][0]["action"], "create_delete_marker")

    def test_noncurrent_uses_successor_time(self):
        old = obj(version_id="old", is_latest=False, noncurrent_since="2026-03-31T12:00:00Z")
        new = obj(version_id="new", last_modified="2026-03-31T12:00:00Z")
        p = {"Rules": [{"ID": "history", "Status": "Enabled", "Filter": {},
                        "NoncurrentVersionExpiration": {"NoncurrentDays": 1}}]}
        r = self.run_preview(p, inventory(old, new, versioning="Enabled"))
        self.assertEqual(len(r["events"]), 1)
        self.assertEqual(r["events"][0]["eligible_at"], "2026-04-02T00:00:00Z")
        self.assertEqual(r["events"][0]["action"], "expire_noncurrent_version")

    def test_sole_marker_cleanup(self):
        p = policy(Expiration={"ExpiredObjectDeleteMarker": True})
        r = self.run_preview(p, inventory(obj(delete_marker=True, size=0), versioning="Enabled"))
        self.assertEqual(r["events"][0]["action"], "remove_delete_marker")

    def test_marker_with_history_is_not_removed(self):
        marker = obj(version_id="marker", delete_marker=True, size=0, last_modified="2026-02-01T12:00:00Z")
        old = obj(is_latest=False, noncurrent_since=marker["last_modified"])
        r = self.run_preview(policy(Expiration={"ExpiredObjectDeleteMarker": True}),
                             inventory(marker, old, versioning="Enabled"))
        self.assertEqual(r["events"], [])

    def test_disabled_rule(self):
        self.assertEqual(self.run_preview(policy(Status="Disabled"))["events"], [])

    def test_prefix(self):
        self.assertEqual(self.run_preview(policy(Filter={"Prefix": "else/"}))["events"], [])

    def test_tag_and_size(self):
        p = policy(Filter={"And": {"Prefix": "logs/", "Tags": [{"Key": "env", "Value": "test"}],
                                    "ObjectSizeGreaterThan": 100, "ObjectSizeLessThan": 200}})
        for size, count in [(100, 0), (101, 1), (199, 1), (200, 0)]:
            with self.subTest(size=size):
                self.assertEqual(len(self.run_preview(p, inventory(obj(size=size, tags={"env": "test"})))["events"]), count)

    def test_transition_size_default_and_override(self):
        p = {"Rules": [{"Status": "Enabled", "Filter": {}, "Transitions": [{"Days": 30, "StorageClass": "STANDARD_IA"}]}]}
        for size, count in [(131071, 0), (131072, 1)]:
            with self.subTest(size=size):
                self.assertEqual(len(self.run_preview(p, inventory(obj(size=size)))["events"]), count)
        p["Rules"][0]["Filter"] = {"ObjectSizeGreaterThan": 0}
        self.assertEqual(len(self.run_preview(p, inventory(obj(size=1)))["events"]), 1)

    def test_absolute_date(self):
        r = self.run_preview(policy(Expiration={"Date": "2026-03-01T00:00:00Z"}))
        self.assertEqual(r["events"][0]["eligible_at"], "2026-03-01T00:00:00Z")

    def test_competing_actions_not_silently_selected(self):
        r = self.run_preview(policy(Transitions=[{"Days": 30, "StorageClass": "GLACIER"}]))
        self.assertEqual(len(r["events"]), 2)
        self.assertEqual(r["competing_candidates"][0]["candidate_count"], 2)

    def test_input_unchanged_and_deterministic(self):
        p, i = policy(), inventory(obj())
        originals = copy.deepcopy((p, i))
        self.assertEqual(simulate(p, i, AS_OF), simulate(p, i, AS_OF))
        self.assertEqual((p, i), originals)

    def test_empty_inventory(self):
        self.assertEqual(self.run_preview(i=inventory())["summary"]["objects_scanned"], 0)

    def test_invalid_policies(self):
        cases = [policy(Expiration={"Days": -1}), policy(Expiration={"Days": True}),
                 policy(Expiration={"Days": 1, "Date": AS_OF}), policy(Expiration={"Date": "2026-01-01T01:00:00Z"}),
                 policy(NoncurrentVersionExpiration={"NoncurrentDays": 1, "NewerNoncurrentVersions": 2}),
                 policy(AbortIncompleteMultipartUpload={"DaysAfterInitiation": 1}),
                 policy(Filter={"Bogus": 1}), policy(Filter={"Prefix": "x", "Tag": {"Key": "a", "Value": "b"}}),
                 policy(Transitions=[{"Days": 1, "StorageClass": "STANDARD_IA"}]),
                 policy(Transitions=[{"Days": 30, "StorageClass": "INTELLIGENT_TIERING"}]),
                 policy(Expiration={"ExpiredObjectDeleteMarker": False}),
                 policy(Filter={"Tag": {"Key": "x", "Value": "y"}}, Expiration={"ExpiredObjectDeleteMarker": True}),
                 policy(Filter={"And": {"Prefix": "x"}}), {"Rules": []}]
        for p in cases:
            with self.subTest(policy=p), self.assertRaises(PreviewError):
                self.run_preview(p)

    def test_invalid_inventories(self):
        cases = [inventory(obj(), complete=False), inventory(obj(), versioning="Suspended"),
                 inventory(obj(), object_lock=True), inventory(obj(), replication=True),
                 inventory(obj(storage_class="GLACIER")), inventory(obj(size=-1)),
                 inventory(obj(last_modified="2026-01-01")), inventory(obj(last_modified="2027-01-01T00:00:00Z")),
                 inventory(obj(), obj()), inventory(obj(is_latest=False)),
                 inventory(obj(noncurrent_since="2026-02-01T00:00:00Z")),
                 inventory(obj(delete_marker=True)), inventory(obj(size=True))]
        for i in cases:
            with self.subTest(inventory=i), self.assertRaises(PreviewError):
                self.run_preview(i=i)

    def test_bad_successor_history(self):
        old = obj(is_latest=False, noncurrent_since="2026-02-02T00:00:00Z")
        new = obj(version_id="v2", last_modified="2026-02-01T00:00:00Z")
        with self.assertRaisesRegex(PreviewError, "successor"):
            self.run_preview(i=inventory(old, new, versioning="Enabled"))

    def test_noncurrent_transition(self):
        new = obj(version_id="v2", last_modified="2026-02-01T00:00:00Z")
        old = obj(is_latest=False, noncurrent_since=new["last_modified"])
        p = {"Rules": [{"Status": "Enabled", "Filter": {}, "NoncurrentVersionTransitions":
                        [{"NoncurrentDays": 30, "StorageClass": "GLACIER"}]}]}
        r = self.run_preview(p, inventory(old, new, versioning="Enabled"))
        self.assertEqual(r["events"][0]["target_storage_class"], "GLACIER")
        self.assertEqual(r["events"][0]["eligible_at"], "2026-03-04T00:00:00Z")
