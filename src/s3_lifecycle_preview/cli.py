"""Local JSON in, report on stdout out. No network, credentials, or mutations."""
import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .engine import PreviewError, simulate


def load(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise PreviewError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline S3 lifecycle snapshot eligibility preview. Never connects to AWS.")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--policy", required=True, help="AWS-style lifecycle Rules JSON file")
    parser.add_argument("--inventory", required=True, help="normalized complete inventory JSON file")
    parser.add_argument("--as-of", required=True, help="explicit ISO-8601 timestamp with timezone")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    parser.add_argument("--fail-on-eligible", action="store_true", help="exit 1 when any candidate is eligible")
    args = parser.parse_args(argv)
    try:
        report = simulate(load(args.policy), load(args.inventory), args.as_of)
    except (PreviewError, OSError, UnicodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=True))
    else:
        print("S3 lifecycle preview — snapshot eligibility, not an execution forecast")
        print(json.dumps(report["summary"], sort_keys=True))
        for event in report["events"]:
            print(f'{event["status"]:9} {event["eligible_at"]} {event["action"]:25} '
                  f'{json.dumps(event["key"])} version={json.dumps(event["version_id"])} '
                  f'rule={json.dumps(event["rule_id"])} target={event.get("target_storage_class", "-")}')
        if report["competing_candidates"]:
            print("Competing eligible actions detected; precedence is not resolved. See support matrix.")
    return 1 if args.fail_on_eligible and report["summary"]["eligible_actions"] else 0
