#!/usr/bin/env python3
"""Simple backlink outreach tracker for seo/backlink-prospects.csv."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict


CSV_PATH = Path(__file__).with_name("backlink-prospects.csv")
LOG_PATH = Path(__file__).with_name("registry-log.csv")


def load_rows() -> List[Dict[str, str]]:
    with CSV_PATH.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def save_rows(rows: List[Dict[str, str]]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def append_log(platform: str, action: str, result: str, details: str = "") -> None:
    file_exists = LOG_PATH.exists()
    with LOG_PATH.open("a", encoding="utf-8", newline="") as f:
        fieldnames = ["ts_utc", "platform", "action", "result", "details"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(
            {
                "ts_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "platform": platform,
                "action": action,
                "result": result,
                "details": details,
            }
        )


def update_platform(
    rows: List[Dict[str, str]],
    platform: str,
    *,
    status: str | None = None,
    profile_url: str | None = None,
    placed_url: str | None = None,
    notes: str | None = None,
) -> bool:
    updated = False
    for row in rows:
        if row["platform"] != platform:
            continue
        if status is not None:
            row["status"] = status
        if profile_url is not None:
            row["profile_url"] = profile_url
        if placed_url is not None:
            row["placed_url"] = placed_url
        if notes is not None:
            row["notes"] = notes
        updated = True
    return updated


def print_summary(rows: List[Dict[str, str]]) -> None:
    by_status: Dict[str, int] = {}
    by_tier: Dict[str, int] = {}
    for row in rows:
        by_status[row["status"]] = by_status.get(row["status"], 0) + 1
        by_tier[row["tier"]] = by_tier.get(row["tier"], 0) + 1

    print("Status:")
    for key in sorted(by_status):
        print(f"  {key}: {by_status[key]}")

    print("Tier:")
    for key in sorted(by_tier):
        print(f"  {key}: {by_tier[key]}")


def print_next(rows: List[Dict[str, str]], limit: int) -> None:
    open_statuses = {"todo", "in_progress", "awaiting_user", "awaiting_user_registration", "awaiting_user_data"}
    queue = [r for r in rows if r["status"] in open_statuses]
    queue.sort(key=lambda r: (int(r["tier"]), 0 if r["priority"] == "high" else 1, r["platform"]))
    for row in queue[:limit]:
        line = (
            f'{row["platform"]} | tier={row["tier"]} | priority={row["priority"]} '
            f'| status={row["status"]} | manual={row["requires_manual_step"]}'
        )
        if row.get("profile_url"):
            line += f" | form={row['profile_url']}"
        print(line)


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage backlink prospects CSV")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("summary", help="Show summary stats")

    p_start = sub.add_parser("start", help="Mark platform as in_progress")
    p_start.add_argument("--platform", required=True)
    p_start.add_argument("--profile-url", default=None)

    p_place = sub.add_parser("mark-placed", help="Mark platform as placed")
    p_place.add_argument("--platform", required=True)
    p_place.add_argument("--placed-url", required=True)
    p_place.add_argument("--profile-url", default=None)

    p_reset = sub.add_parser("reset", help="Reset platform to todo")
    p_reset.add_argument("--platform", required=True)

    p_next = sub.add_parser("next", help="Show next platforms to process")
    p_next.add_argument("--limit", type=int, default=10)

    p_log = sub.add_parser("log", help="Append registry attempt log")
    p_log.add_argument("--platform", required=True)
    p_log.add_argument("--action", required=True)
    p_log.add_argument("--result", required=True)
    p_log.add_argument("--details", default="")

    p_set = sub.add_parser("set", help="Set status and optional fields")
    p_set.add_argument("--platform", required=True)
    p_set.add_argument("--status", required=True)
    p_set.add_argument("--profile-url", default=None)
    p_set.add_argument("--placed-url", default=None)
    p_set.add_argument("--notes", default=None)

    args = parser.parse_args()
    rows = load_rows()

    if args.cmd == "summary":
        print_summary(rows)
        return
    if args.cmd == "next":
        print_next(rows, args.limit)
        return
    if args.cmd == "log":
        append_log(args.platform, args.action, args.result, args.details)
        print(f"Logged: {args.platform} [{args.result}]")
        return

    if args.cmd == "set":
        ok = update_platform(
            rows,
            args.platform,
            status=args.status,
            profile_url=args.profile_url,
            placed_url=args.placed_url,
            notes=args.notes,
        )
        if not ok:
            raise SystemExit(f"Platform not found: {args.platform}")
        save_rows(rows)
        print(f"Updated: {args.platform} -> {args.status}")
        return

    if args.cmd == "start":
        ok = update_platform(
            rows,
            args.platform,
            status="in_progress",
            profile_url=args.profile_url,
        )
    elif args.cmd == "mark-placed":
        ok = update_platform(
            rows,
            args.platform,
            status="placed",
            profile_url=args.profile_url,
            placed_url=args.placed_url,
        )
    else:
        ok = update_platform(rows, args.platform, status="todo", profile_url="", placed_url="")

    if not ok:
        raise SystemExit(f"Platform not found: {args.platform}")

    save_rows(rows)
    print(f"Updated: {args.platform}")


if __name__ == "__main__":
    main()
